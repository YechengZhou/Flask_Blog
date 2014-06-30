#/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'yechengzhou'
from flask import Flask, url_for, request, make_response, render_template, session, escape, redirect
from www.models import User, Blog, Comment
import time
from db import db

db.create_engine(user='root', password='ZYC06091126!', database='yecheng')

DEBUG = True
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
USERNAME = 'root'
PASSWORD = 'ZYC06091126!'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

print app.config

'''
url design:
/blog/: display all articles with brief introduction
/blog/<id>: display the specific article, including it's comments

/projects/: list all my project in Github

/about/: a introduction of myself


'''

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return redirect('/login/')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    # 如果会话中有用户名就删除它。
    session.pop('username', None)
    return redirect(url_for('index'))

#####################################################
@app.route('/')
def home():
    # get user info and blog info
    return render_template('home.html')



@app.route('/blog/')
def show_all_blog():
    entries = db.select('select * from blogs')
    for i in entries:
        i['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i['created_at']))
    return render_template('blog.html', entries=entries)


if __name__ == '__main__':
    app.run(port=9999)