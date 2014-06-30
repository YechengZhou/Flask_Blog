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


blog = Blog(
    user_id = '00140408322081006c255e61b634c5a8937be2afc6119f7000',
    user_name = 'Test',
    user_image = 'about:blank',
    name = '测试文章',
    summary = '一个好的应用和用户界面都需要良好的反馈。',
    content = '一个好的应用和用户界面都需要良好的反馈。如果用户得不到足够的反馈，那么应用最终 会被用户唾弃。 Flask 的闪现系统提供了一个良好的反馈方式。闪现系统的基本工作方式 是：在且只在下一个请求中访问上一个请求结束时记录的消息。一般我们结合布局模板来 使用闪现系统。',

)

blog.insert()
'''
blogs = db.select('select * from blogs')

print blogs

