#/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'yechengzhou'

"""
JSON API definition
"""

from flask import Flask
from flask.ext.restful import Resource, Api
from db import db

app = Flask(__name__)
api = Api(app)

db.create_engine(user='root', password='ZYC06091126!', database='yecheng')


class Blog(Resource):
    """
    get 1 blog information by id
    """
    def get(self, blog_id):
        result = db.select("select * from blogs where id='%s'" % blog_id)
        return result[0]

api.add_resource(Blog, '/api/blog/<string:blog_id>')


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

api.add_resource(AllBlog, '/api/allblog/')


if __name__ == '__main__':
    app.run(debug=True)
