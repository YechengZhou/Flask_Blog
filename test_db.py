#!/usr/bin python
# -*- coding: utf-8 -*-
__author__ = 'yechengzhou'

from www.models import User, Blog, Comment

from db import db

db.create_engine(user='root', password='ZYC06091126!', database='yecheng')
'''
u = User(name='Test', email='test@example.com', password='1234567890', image='about:blank')

u.insert()

print 'new user id:', u.id

u1 = User.find_first('where email=?', 'test@example.com')
print 'find user\'s name:', u1.name

u1.delete()

u2 = User.find_first('where email=?', 'test@example.com')
print 'find user:', u2
'''

blog = Blog(
    user_id = '00140408322081006c255e61b634c5a8937be2afc6119f7000',
    user_name = 'Test',
    user_image = 'about:blank',
    name = '我了个去',
    summary = '编写后端Python代码不但很简单，而且非常容易测试',
    content = '编写后端Python代码不但很简单，而且非常容易测试，上面的API：api_create_blog()本身只是一个普通函数。\
Web开发真正困难的地方在于编写前端页面。前端页面需要混合HTML、CSS和JavaScript，如果对这三者没有深入地掌握，编写的前端页面将很快难以维护。\
更大的问题在于，前端页面通常是动态页面，也就是说，前端页面往往是由后端代码生成的。'

)

blog.insert()

blogs = db.select('select * from blogs')

print blogs

