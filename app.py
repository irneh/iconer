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

def make_variants(orignameext, filepathnameext):
  newpathname, ext = os.path.splitext(filepathnameext)
  zippathnameext = newpathname + '.zip'
  origname = os.path.splitext(orignameext)[0]
  variants = [(1024, 1024, 1), (152, 152, 1), (120,120, 2), (120,120, 1), (114, 114, 1), (80, 80, 1), (76, 76, 1), (72, 72, 1), (58, 58, 1), (57, 57, 1), (50, 50, 1), (44, 44, 1), (29, 29, 1), (25, 25, 1), (22, 22, 1)]
  orig = wi.Image(filename=filepathnameext)
  imagezip = zipfile.ZipFile(zippathnameext, 'a')
  imagezip.write(filepathnameext, orignameext)
  for w, h, x in variants:
    mod = x > 1 and '@' + str(x) + 'x' or ''
    clonepathnameext = newpathname + '-' + str(w) + 'x' + str(h) + mod + ext
    zipnameext = origname + '-' + str(w) + 'x' + str(h) + mod + ext
    clone = orig.clone()
    clone.resize(w * x, h * x)
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
  url = make_variants(i.filename, images.path(iname))
  return f.render_template('download.html', url=url)

if __name__ == '__main__':
  app.run()
