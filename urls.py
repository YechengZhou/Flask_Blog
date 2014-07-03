#/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'yechengzhou'
from flask import Flask, url_for, request, make_response, render_template, session, escape, redirect
from www.models import User, Blog, Comment
import time
from db import db
import urllib2
import logging
import json

if db.engine:
    logging.info("db engine already exits")
else:
    db.create_engine(user='root', password='ZYC06091126!', database='yecheng')

DEBUG = True
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
USERNAME = 'root'
PASSWORD = 'ZYC06091126!'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

print app.config

for i in app.config.items():
    logging.info('%s : %s' % (i[0], i[1]))

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
    return redirect(url_for('blog'))


@app.route('/blog/')
def show_all_blog():
    entries = db.select('select * from blogs')
    for i in entries:
        i['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i['created_at']))
    return render_template('blog.html', entries=entries)


@app.route('/blog/<string:id>')
def show_article(id):
    this_entry = db.select("select * from blogs where id='%s'" % id)[0]
    this_entry['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(this_entry['created_at']))
    return render_template('article.html', entry=this_entry)


@app.route('/projects/')
def show_projects():
    """
    call github api to get all repositories
    """
    url = 'https://api.github.com/users/YechengZhou/repos'
    all_rep = git_api_query(url)
    all_repositories_info = []
    if isinstance(all_rep, list):
        for i in all_rep:
            logging.info("query url is : %s" % i['url'])
            i_result = git_api_query(i['url'])
            this_rep = db.MyDict()
            if isinstance(i_result, dict):
                this_rep['name'] = i_result['name']
                this_rep['html_url'] = i_result['html_url']
                this_rep['description'] = i_result['description']
                all_repositories_info.append(this_rep)
    return render_template('projects.html', projects=all_repositories_info)


def git_api_query(url):
    """
    :param url: api url
    :return: query result
    """
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    return json.loads(response.read())


@app.route('/create_blog/')
def create_blog():
    """
    create blog and add  to DB
    """
    return render_template('create_blog.html', action='/api/addblog/')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    from www import RESTAPI
    RESTAPI.add_res(app)
    app.run(port=9999)