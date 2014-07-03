#/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'yechengzhou'

"""
JSON API definition
"""

from flask import Flask, request
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
        print request.form
        blog = Blog(
            user_id = '00140408322081006c255e61b634c5a8937be2afc6119f7000',
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