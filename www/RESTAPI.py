#/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'yechengzhou'

"""
JSON API definition
"""

from flask import request
from flask.ext.restful import Resource, Api
from db import db
import logging
import uuid
from www.models import User, Blog, Comment
import www.constant as Constant
import smtplib

"""
if 'app' in locals().keys():
    logging.info("app already exits")
else:
    app = Flask(__name__)
"""

if db.engine:
    logging.info("db engine already exists")
else:
    db.create_engine(user='root', password='ZYC06091126!', database='yecheng')


class APIError(StandardError):
    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


class APIValueError(APIError):
    '''
    Indicate the input value has error or invalid. The data specifies the error field of input form.
    '''
    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)


class APIResourceNotFoundError(APIError):
    '''
    Indicate the resource was not found. The data specifies the resource name.
    '''
    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)


class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    '''
    def __init__(self, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)


class SingleBlog(Resource):
    """
    get 1 blog information by id
    """
    def get(self, blog_id):
        result = db.select("select * from blogs where id='%s'" % blog_id)
        return result[0]


class AllBlog(Resource):
    """
    get all blogs
    """
    def get(self):
        results = db.select("select * from blogs")
        result_dict = {}
        for i in range(len(results)):
            result_dict[str(i)] = results[i]
        return result_dict


class AddBlog(Resource):
    """
    add new blog
    """
    def post(self):
        #print request.form
        """
        try:
            print session['name']
        except:
            print 'Add blog has no username'
        """
        tag_list = []
        this_blog_name = request.form['name']
        for i in Constant.tags:
            if this_blog_name.lower().find(i) != -1:
                tag_list.append(i)

        blog = Blog(
            user_id='00140408322081006c255e61b634c5a8937be2afc6119f7000',  # TODO
            user_name='Test',
            tag=";".join(tag_list),
            name=request.form['name'],
            summary=request.form['summary'],
            content=request.form['content'],
        )
        blog.insert()


class AddComments(Resource):
    """
    add comments to blog
    """
    def post(self):
        user_url = ""
        if len(request.form['url']) != 0:
            if not (request.form['url'].__contains__("http://") or request.form['url'].__contains__("https://")):
                user_url = "http://" + request.form['url']
            else:
                user_url = request.form['url']

        this_content = request.form["content"]
        if this_content[0] == "@":  # 此评论为回复评论
            temp_dict = {}
            for i in (" ", "\t", "\n"):  # 分离评论回复内容和回复人
                find_result_tmp = this_content.find(i)
                if find_result_tmp != -1:
                    temp_dict[i] = find_result_tmp
            if len(temp_dict) != 0:
                # 按value 排序，得到第一个空白符的位置
                x, first_space = sorted(temp_dict.items(), key=lambda temp_dict:temp_dict[1])[0]
                if first_space:
                    # get the author he want to reply
                    reply_author = this_content[1:first_space]
                else:
                    reply_author = this_content[1:]
                    print "reply: ", reply_author


        # send email to replied user TODO


        comment = Comment(
            blog_id=request.form['blog_id'],
            user_id=(str(uuid.uuid4()).replace("-","")*2)[:50], # 随机生成一个userid， 不提供用户注册功能了，没意义
            user_name=request.form['author'],
            user_email=request.form['email'],
            user_url=user_url,
            content=this_content,
        )
        comment.insert()


class Register(Resource):
    """
    register user
    """
    def post(self):
        t = db.select("select * from users where email=?", request.form['email'])
        if t:
            raise APIValueError(data=request.form['email'], message="email has already been registered")
        user = User(
            email=request.form['email'],
            password=request.form['password'],
            name=request.form['username'],
            image=request.form['image'] if request.form.has_key('image') else "about:blank",
            admin=1,
        )
        user.insert()


def add_res(app):
    api = Api(app)
    api.add_resource(SingleBlog, '/api/blog/<string:blog_id>')
    api.add_resource(AllBlog, '/api/allblog/')
    api.add_resource(AddBlog, '/api/addblog/')
    api.add_resource(AddComments, '/api/addcomment/')
    #api.add_resource(Register, '/api/register/')

if __name__ == '__main__':
    #app.run(debug=True)
    pass