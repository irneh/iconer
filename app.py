from variants import variants
import boto
import flask as f
import flask.ext.uploads as fu
import os
import uuid
import wand.image as wi
import zipfile

app = f.Flask(__name__)
app.debug = os.getenv('APP_DEBUG')

## Flask-Uploads config.
app.config['UPLOADED_IMAGES_DEST'] = 'tmp'
images = fu.UploadSet('images', ('gif', 'bmp', 'png', 'jpg', 'jpeg'))
fu.configure_uploads(app, (images))

## S3
S3_BUCKET = os.getenv('S3_BUCKET')
c = boto.connect_s3()
b = c.get_bucket(S3_BUCKET)
k = boto.s3.key.Key(b)

def make_zip(orig_path, new_name, use_apple_names):
  def make_variant(orig, w, h, new_name):
    clone = orig.clone()
    clone.resize(w, h)
    clone.save(filename=new_name)

  def zip_obj(zf, obj, arcname):
    zf.write(obj, arcname)
    os.remove(obj)

  path, ext = os.path.splitext(new_name)
  zip_name = path + '.zip'
  orig_name = os.path.splitext(orig_path)[0]

  ## Write original into new zipfile.
  zf = zipfile.ZipFile(zip_name, 'a')
  zf.write(new_name, orig_path)

  ## Create image Object.
  orig = wi.Image(filename=new_name)
  os.remove(new_name)

  for w, h, apple_name, name in variants:
    ## Figure out what to name the files in the zip
    if use_apple_names:
      arcname = apple_name + ext
    else:
      arcname = orig_name + '-' + name + ext
    variant_name = path + '-' + name + ext
    ## Write variants to disk then move into zip
    make_variant(orig, w, h, variant_name)
    zip_obj(zf, variant_name, arcname)

  zf.close()
  return zip_name

@app.route('/', methods=['GET', 'POST'])
def index():
  if f.request.method == 'GET':
    return f.render_template('index.html')
  else:
    ## Process incoming args
    img = f.request.files['image']
    use_apple_names = 'use_apple_names' in f.request.form
    ## Save incoming file to Flask-Uploads collection and local disk.
    localname = str(uuid.uuid4()) + os.path.splitext(img.filename)[1]
    images.save(img, None, localname)
    ## Render variants into zipfile
    zipname = make_zip(img.filename, images.path(localname), use_apple_names)
    ## Move zipfile to S3
    k.key = os.path.basename(zipname)
    k.set_contents_from_filename(zipname)
    os.remove(zipname)
    ## Return URL to S3 zipfile
    url = 'http://' + S3_BUCKET + '/' + os.path.basename(zipname)
    return f.render_template('download.html', url=url)

if __name__ == '__main__':
  app.run()
