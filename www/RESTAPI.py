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
from www.models import User, Blog, Comment as d

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
        super(APIError,self).__init__(message)
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
        blog = Blog(
            user_id = '00140408322081006c255e61b634c5a8937be2afc6119f7000',  # TODO
            user_name = 'Test',
            user_image = 'about:blank',
            name = request.form['name'],
            summary = request.form['summary'],
            content = request.form['content'],
        )
        blog.insert()


def add_res(app):
    api = Api(app)
    api.add_resource(SingleBlog, '/api/blog/<string:blog_id>')
    api.add_resource(AllBlog, '/api/allblog/')
    api.add_resource(AddBlog, '/api/addblog/')

if __name__ == '__main__':
    #app.run(debug=True)
    pass