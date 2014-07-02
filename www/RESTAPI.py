#/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'yechengzhou'

"""
JSON API definition
"""

from flask import Flask, request
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
            name = '测试文章',
            summary = '一个好的应用和用户界面都需要良好的反馈。',
            content = '一个好的应用和用户界面都需要良好的反馈。如果用户得不到足够的反馈，那么应用最终 会被用户唾弃。 Flask 的闪现系统提供了一个良好的反馈方式。闪现系统的基本工作方式 是：在且只在下一个请求中访问上一个请求结束时记录的消息。一般我们结合布局模板来 使用闪现系统。',
        )

        #blog.insert()

api.add_resource(AddBlog, '/api/addblog/')


if __name__ == '__main__':
    app.run(debug=True)
