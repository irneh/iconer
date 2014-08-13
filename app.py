## Local file.

from variants import variants

## Normal imports.

import flask as f
import flask.ext.uploads as fu
import os
import uuid
import wand.image as wi
import zipfile

## Start me up.

app = f.Flask(__name__)
app.debug = True

## Flask-Uploads config.

app.config['UPLOADED_IMAGES_DEST'] = 'static'
images = fu.UploadSet('images', ('gif', 'bmp', 'png', 'jpg', 'jpeg'))
fu.configure_uploads(app, (images))

## Codez

def uuname(filename):
  name = str(uuid.uuid4())
  ext = os.path.splitext(filename)[1]
  return name + ext

def make_variants(ofile, nname, anames):
  path, ext = os.path.splitext(nname)
  zname = path + '.zip'
  oname = os.path.splitext(ofile)[0]
  orig = wi.Image(filename=nname)
  imagezip = zipfile.ZipFile(zname, 'a')
  imagezip.write(nname, ofile)
  for w, h, an, n in variants:
    cname = path + '-' + n + ext
    if anames:
      zipnameext = an + ext
    else:
      zipnameext = oname + '-' + n + ext
    clone = orig.clone()
    clone.resize(w, h)
    clone.save(filename=cname)
    imagezip.write(cname, zipnameext)
    os.remove(cname)
  imagezip.close()
  os.remove(nname)
  return zname

@app.route('/', methods=['GET', 'POST'])
def index():
  if f.request.method == 'GET':
    return f.render_template('upload.html')
  else:
    img = f.request.files['image']
    anames = 'use_apple_names' in f.request.form
    img_name = uuname(img.filename)
    images.save(img, None, img_name)
    url = make_variants(img.filename, images.path(img_name), anames)
    return f.render_template('download.html', url=url)

if __name__ == '__main__':
  app.run()
