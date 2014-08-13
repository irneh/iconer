## Local file.

from variants import variants

## Normal imports.

import boto
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

app.config['UPLOADED_IMAGES_DEST'] = 'tmp'
images = fu.UploadSet('images', ('gif', 'bmp', 'png', 'jpg', 'jpeg'))
fu.configure_uploads(app, (images))

## S3

S3_BUCKET = os.getenv('S3_BUCKET')
c = boto.connect_s3()
b = c.get_bucket(S3_BUCKET)
k = boto.s3.key.Key(b)

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
  k.key = os.path.basename(zname)
  k.set_contents_from_filename(zname)
  os.remove(nname)
  os.remove(zname)
  return os.path.basename(zname)

@app.route('/', methods=['GET', 'POST'])
def index():
  if f.request.method == 'GET':
    return f.render_template('index.html')
  else:
    img = f.request.files['image']
    anames = 'use_apple_names' in f.request.form
    img_name = uuname(img.filename)
    images.save(img, None, img_name)
    zname = make_variants(img.filename, images.path(img_name), anames)
    url = 'http://' + S3_BUCKET + '/' + zname
    return f.render_template('download.html', url=url)

if __name__ == '__main__':
  app.run()
