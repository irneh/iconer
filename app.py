import flask as f
import flask.ext.uploads as fu
import os
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

@app.route('/upload/')
def upload():
  return f.render_template('upload.html')

@app.route('/receive', methods = ['GET', 'POST'])
def receive():
  i = f.request.files['image']
  iname = uuname(i.filename)
  images.save(i, None, iname)
  return f.redirect(f.url_for('index'))

if __name__ == '__main__':
  app.run()
