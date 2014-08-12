import flask as f
import flask.ext.uploads as fu
import os
import uuid
import wand.image as wi
import zipfile

app = f.Flask(__name__)
app.debug = True

app.config['UPLOADED_IMAGES_DEST'] = 'static'
images = fu.UploadSet('images', ('png'))
fu.configure_uploads(app, (images))

def uuname(filename):
  name = str(uuid.uuid4())
  ext = os.path.splitext(filename)[1]
  return name + ext

def make_variants(orignameext, filepathnameext):
  newpathname, ext = os.path.splitext(filepathnameext)
  zippathnameext = newpathname + '.zip'
  origname = os.path.splitext(orignameext)[0]
  variants = [(1024, 1024), (152, 152), (120,120), (114, 114), (80, 80), (76, 76), (72, 72), (58, 58), (57, 57), (50, 50), (44, 44), (29, 29), (25, 25), (22, 22)]
  orig = wi.Image(filename=filepathnameext)
  imagezip = zipfile.ZipFile(zippathnameext, 'a')
  imagezip.write(filepathnameext, orignameext)
  for w, h in variants:
    clonepathnameext = newpathname + '-' + str(w) + 'x' + str(h) + '.' + ext
    zipnameext = origname + '-' + str(w) + 'x' + str(h) + '.' + ext
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
  url = make_variants(i.filename, images.path(iname))
  return f.render_template('download.html', url=url)

if __name__ == '__main__':
  app.run()
