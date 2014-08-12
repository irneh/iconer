import flask as f
import flask.ext.uploads as fu
import os
import subprocess
import uuid

app = f.Flask(__name__)
app.debug = True

app.config['UPLOADED_IMAGES_DEST'] = 'images'
images = fu.UploadSet('images', ('png'))
fu.configure_uploads(app, (images))

def uuname(filename):
  name = str(uuid.uuid4())
  ext = os.path.splitext(filename)[1]
  return name + ext

@app.route('/')
def index():
  return 'hi'

@app.route('/shell')
def shell():
  return subprocess.check_output(['convert', '--help'])

@app.route('/upload/')
def upload():
  return f.render_template('upload.html')

@app.route('/receive', methods = ['GET', 'POST'])
def receive():
  i = f.request.files['image']
  iname = uuname(i.filename)
  images.save(i, None, iname)
  return f.redirect(f.url_for('index'))

@app.route('/wand')
def wand():
  from wand.image import Image
  with Image(filename='image.png') as img:
    for r in 1, 2, 3:
      with img.clone() as i:
        i.resize(int(i.width * r * 0.25), int(i.height * r * 0.25))
        i.rotate(90 * r)
        i.save(filename='image{0}.png'.format(r))

if __name__ == '__main__':
  app.run()
