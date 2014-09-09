# /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'yechengzhou'
from flask import Flask, url_for, request, make_response, render_template, session, escape, redirect
from www.models import User, Blog, Comment
import time
from db import db
import urllib2
import logging
import json
from www.models import Projects

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

/catalog/<datetime(month:201409)>: display blog list for this month
/tag/<tag_name>: display blog list of corresponding tag
'''

logging.basicConfig(level=logging.DEBUG)
from www import RESTAPI
RESTAPI.add_res(app)


# get tags module and catalog module to serve all kinds of pages
all_blogs = db.select("select * from blogs order by created_at")
time_list = []
catalogs = []
for this_blog in all_blogs:
    this_blog['created_at'] = time.strftime("%Y%m", time.localtime(this_blog['created_at']))
    #catalogs.append(db.MyDict(('date','url'),(this_blog['created_at'], "/catalog/" + str(this_blog['created_at']))))
    time_list.append(this_blog['created_at'])
time_list = list(set(time_list))
for this_time in time_list:
    catalogs.append(db.MyDict(('date', 'url', 'num'),(this_time[0:4]+" - " + this_time[4:], "/catalog/" + str(this_time), 0)))

for this_cata in catalogs:
    for j in all_blogs:
        if j['created_at'] == "".join(this_cata.date.split(" - ")):
            this_cata.num += 1

catalogs.sort(reverse=True)


class LoginError(StandardError):
    def __init__(self, error, data='', message=''):
        super(LoginError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


@app.route('/')
def index():
    """
    if session.has_key('login') and session['login'] and session.has_key('email') and session.has_key('password'):
        logging.info('Logged in as %s' % escape(session['email']))
        return redirect('/blog/')
    """
    return redirect('/blog/')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.has_key('login') and session['login'] and session.has_key('username'):
            return redirect('/')
        return render_template('login.html')

    elif request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = db.select_first_one('select * from users where email=?', email)
        if user is None:
            raise LoginError('auth:failed', 'email', 'email invalid')
            #print 'user do not exits'
        elif user.password != password:
            raise LoginError('auth:failed', 'password', 'Invalid password.')
            #print 'password incorrect'
        session['login'] = True
        session['email'] = email
        session['username'] = user.name
        session['password'] = password
        return redirect('/')


@app.route('/logout/')
def logout():
    # 如果会话中有用户名就删除它。
    session.pop('username', None)
    session['login'] = False
    return redirect(url_for('index'))


@app.route('/register/')
def register():
    return render_template('register.html', redirect="/login/", action='/api/register/')

glob_username = None


def checklogin(func):
    def wrapper(*args, ** kwargs):
        if session.has_key('username'):
            glob_username = session['username']
            logging.info("User glob_username logged in")
        else:
            glob_username = None
        return func(*args, ** kwargs)
    return wrapper

#####################################################


@app.route('/')
def home():
    # get user info and blog info
    return redirect(url_for('blog'))


@app.route('/blog/')
def show_all_blog():
    entries = db.select('select * from blogs order by created_at DESC')
    for i in entries:
        i['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i['created_at']))
    if session.has_key('username'):
        return render_template('blog.html', entries=entries, username=session['username'], catalogs=catalogs)
    else:
        return render_template('blog.html', entries=entries, catalogs=catalogs)


@app.route('/blog/<string:id>')
def show_article(id):
    all_entries = db.select("select * from blogs order by created_at" )
    for i in all_entries:
        if i['id'] == id:
            this_entry = i
            this_entry_index = all_entries.index(i)
            if this_entry_index > 0:
                next_entry = all_entries[this_entry_index-1]
            else:
                next_entry = None
            if this_entry_index < (len(all_entries) -1):
                pre_entry = all_entries[this_entry_index+1]
            else:
                pre_entry = None
    #this_entry = db.select("select * from blogs where id='%s'" % id)[0]
    this_entry['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(this_entry['created_at']))
    this_comments = db.select("select * from comments where blog_id ='%s'" % id)
    if this_comments:
        for i in this_comments:
            i.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i.created_at))

    if session.has_key('username'):
        return render_template('article.html', entry=this_entry, username=session['username'], comments=this_comments, pre_entry=pre_entry, next_entry=next_entry, catalogs=catalogs)
    else:
        return render_template('article.html', entry=this_entry, comments=this_comments, pre_entry=pre_entry, next_entry=next_entry, catalogs=catalogs)


#@checklogin
@app.route('/projects/')
def show_projects():
    """
    call github api to get all repositories
    """
    #global glob_username
    url = 'https://api.github.com/users/YechengZhou/repos'
    last_update_time = db.select('select created_at from projects limit 0,1;')
    all_repositories_info = []
    print last_update_time

    if len(last_update_time) != 0 and int(time.time()) - int(last_update_time[0].created_at) < 3600 * 12:  # do not update within 12 hours
        all_repositories_info = db.select('select * from projects')
    else:
        all_rep = git_api_query(url)
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
        #if len(last_update_time) == 0: # no project items currently, just insert what have got
            #flag_just_insert = True
        # update project schema based on new query result from Github api
        all_repo_name_db = db.select('select name from projects;')

        for p in all_repositories_info:
            if db.MyDict(('name',), (p.name,)) in all_repo_name_db:  # just update
                db.update("update projects set url=?, description=?, created_at=? where name=?", p['html_url'], p['description'], time.time(), p.name)
            else:
                this_project = Projects(
                    name=p['name'],
                    url=p['html_url'],
                    description=p['description']
                )
                this_project.insert()

    if session.has_key('username'):
        #dir(all_repositories_info[0])
        return render_template('projects.html', projects=all_repositories_info, username=session['username'])
    else:
        return render_template('projects.html', projects=all_repositories_info)

    #print glob_username
    #return render_template('projects.html', projects=all_repositories_info, username=glob_username)


def git_api_query(url):
    """

    :rtype : object
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
    if session.has_key('username'):
        return render_template('create_blog.html', action='/api/addblog/', redirect='/blog/', username=session['username'])
    else:
        return render_template('create_blog.html', action='/api/addblog/', redirect='/blog/')

@app.route('/about/')
def about():
    if session.has_key('username'):
        return render_template('about.html', username=session['username'])
    else:
        return render_template('about.html')

if __name__ == '__main__':

    app.run(port=9999)