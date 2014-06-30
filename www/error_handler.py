#/usr/bin/python
__author__ = 'yechengzhou'
from flask import render_template, Flask

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

