import os
import flask as f
from wand.image import Image
from wand.display import display

app = f.Flask(__name__)
app.debug = True

@app.route('/')
def hello_world():
  return os.listdir('.')[4]

@app.route('/wand')
def wand():
  with Image(filename='image.png') as img:
    for r in 1, 2, 3:
      with img.clone() as i:
        i.resize(int(i.width * r * 0.25), int(i.height * r * 0.25))
        i.rotate(90 * r)
        i.save(filename='image-{0}.png'.format(r))
  return 'Done!'

if __name__ == '__main__':
  app.run()
