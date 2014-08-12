import flask as f
import flask.ext.uploads as fu
import os
import uuid
import wand.image as wi
import zipfile

app = f.Flask(__name__)
app.debug = True

app.config['UPLOADED_IMAGES_DEST'] = 'static'
images = fu.UploadSet('images', ('gif', 'bmp', 'png', 'jpg', 'jpeg'))
fu.configure_uploads(app, (images))

def uuname(filename):
  name = str(uuid.uuid4())
  ext = os.path.splitext(filename)[1]
  return name + ext

def make_variants(orignameext, filepathnameext, apple_names):
  newpathname, ext = os.path.splitext(filepathnameext)
  zippathnameext = newpathname + '.zip'
  origname = os.path.splitext(orignameext)[0]
  variants = [
    (1024, 1024, 'iTunesArtwork@2x', '512@2x'),
    (512, 512, 'iTunesArtwork', '512'),
    (152, 152, 'Icon-76@2x', '76@2x'),
    (144, 144, 'Icon-72@2x', '72@2x'),
    (120, 120, 'Icon-60@2x', '60@2x'),
    (114, 114, 'Icon-72@2x', '72@2x'),
    (100, 100, 'Icon-Small-50@2x', '50@2x'),
    (80, 80, 'Icon-Small-40@2x', '40@2x'),
    (76, 76, 'Icon-76', '76'),
    (72, 72, 'Icon-72', '72'),
    (58, 58, 'Icon-Small@2x', '29@2x'),
    (57, 57, 'Icon', '57'),
    (50, 50, 'Icon-Small-50', '50'),
    (40, 40, 'Icon-Small-40', '40'),
    (29, 29, 'Icon-Small', '29')]
  orig = wi.Image(filename=filepathnameext)
  imagezip = zipfile.ZipFile(zippathnameext, 'a')
  imagezip.write(filepathnameext, orignameext)
  for w, h, an, n in variants:
    clonepathnameext = newpathname + '-' + n + ext
    if apple_names:
      zipnameext = an + ext
    else:
      zipnameext = origname + '-' + n + ext
    clone = orig.clone()
    clone.resize(w, h)
    clone.save(filename=clonepathnameext)
    imagezip.write(clonepathnameext, zipnameext)
    os.remove(clonepathnameext)
  imagezip.close()
  os.remove(filepathnameext)
  return zippathnameext

@app.route('/')
def index():
  return f.render_template('upload.html')

@app.route('/upload/')
def upload():
  return f.render_template('upload.html')

@app.route('/receive', methods = ['GET', 'POST'])
def receive():
  i = f.request.files['image']
  iname = uuname(i.filename)
  images.save(i, None, iname)
  url = make_variants(i.filename, images.path(iname), 'apple_names' in f.request.form)
  return f.render_template('download.html', url=url)

if __name__ == '__main__':
  app.run()
