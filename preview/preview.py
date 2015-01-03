from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from glob import glob
import logging


app = Flask(__name__, static_url_path='/tmp', static_folder='tmp')
log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)
handler = RotatingFileHandler('preview.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)


@app.route("/")
def index():
    items = sorted([ i[4:] for i in glob('tmp/*_population') ])
    return render_template('index.html', items=items)


@app.route("/config/<config>")
def config(config):
    items = sorted([ '/'+i for i in glob('tmp/%s/*png' % config) ])
    return render_template('items.html', items=items)


if __name__ == "__main__":
    app.debug = True
    app.run()