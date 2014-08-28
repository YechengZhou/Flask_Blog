# -*- coding: utf-8 -*-
__author__ = 'zhouyecheng'

from sgmllib import SGMLParser
import urllib2, urllib
import logging
from db import db
import re
import time

if db.engine:
    logging.info("db engine already exists")
else:
    db.create_engine(user='root', password='ZYC06091126!', database='yecheng')



class blog_link_getter(SGMLParser):

    def reset(self):
        SGMLParser.reset(self)
        self.urls = []
        self.titles = []
        self.in_div = False
        self.in_a = False

    def start_div(self, attrs):
        for k, v in attrs:
            if k == "class" and v == "postTitle":
                self.in_div = True

    def end_div(self):
        self.in_div = False
        # check if title and urls are corresponded
        if len(self.titles) != len(self.urls):
            logging.warn("titles and urls of articles isn't corresponded!")

    def start_a(self, attrs):
        """
        get linkes
        """
        if self.in_div:
            for k, v in attrs:
                if k == "href":
                    self.urls.append(v)
                    self.in_a = True

    def end_a(self):
        self.in_a = False

    def handle_data(self, data):
        """
        get the article titles
        """
        if self.in_a:
            data.strip()
            self.titles.append(data)


class blog_content_getter(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.blog_content = None

    def feed(self, data):
        start_index = data.find('<div id="cnblogs_post_body">')
        end_index = data.find('<div id="MySignature">')
        self.blog_content = data[start_index:end_index]


class blog_tag_getter(SGMLParser):  # 页面源文件的EntryTag div里面没有a标签...
    def reset(self):
        SGMLParser.reset(self)
        self.cnblog_list_page_url = "http://www.cnblogs.com/ethanchou/default.html?OnlyTitle=1"
        self.tags = []
        self.urls = []
        self.in_tag_div = False
        self.in_a = False
        self.tag_bloglink_dic = {}

    def feed_self(self):
        self.feed(urllib2.urlopen(self.cnblog_list_page_url).read())

    def start_div(self, attrs):
        for k, v in attrs:
            if k == 'class' and v == 'catListTag':
                self.in_tag_div = True

    def end_div(self):
        self.in_tag_div = False

    def start_a(self, attrs):
        valid_a = False
        for k, v in attrs:
            if k == 'href':
                valid_a = True
                self.urls.append(v)

        if self.in_tag_div and valid_a:
            self.in_a = True

    def end_a(self):
        self.in_a = False

    def handle_data(self, data):
        if self.in_a:
            self.tags.append(data)

    def get_specified_tag_blogs(self,):
        if len(self.tags) == len(self.urls):
            for i in range(len(self.urls)):
                this_key = i.replace('%20'," ").split("/")[-2]
                self.tag_bloglink_dic[this_key] = []
                this_content = urllib2.urlopen(self.urls[i]).read()
                j = 0
                while this_content.find('PostsList1_rpPosts_TitleUrl') != -1:
                    temp_idx = this_content.find('PostsList1_rpPosts_TitleUrl_' + str(j))
                    end_idx = this_content.find('>', temp_idx)
                    this_pattern = re.compile(r"http:\/\/www.cnblogs.com\/ethanchou\/p\/\d+\.html")
                    print this_pattern.match(this_content[temp_idx:end_idx]).group(0)
                    #this_list.append(this_pattern.match(this_content[temp_idx:end_idx]).group(0))
                    self.tag_bloglink_dic[this_key].append(this_pattern.match(this_content[temp_idx:end_idx]).group(0))
                    this_content = this_content[end_idx+1:]


class cnblog_getter(object):
    def __init__(self, userid="ethanchou"):
        self.cnblog_list_page_url = "http://www.cnblogs.com/%s/default.html?OnlyTitle=1&page=" % userid
        self.blog_urls = {}
        self.blog_contents = {}
        self.blog_post_time = {}
        self.blog_tags = {}

    def get_blog_link(self):
        i = 1
        while True:
            try:
                url_handler = urllib2.urlopen(self.cnblog_list_page_url + str(i))
                content = url_handler.read()
                url_handler.close()
                blg = blog_link_getter()
                blg.feed(content)
                temp_titles = blg.titles
                temp_urls = blg.urls
                if len(temp_titles) != len(temp_urls):
                    logging.error("blog link getter got un-corresponded titles and links")
                    raise BaseException("blog's title and link un-corresponded")
                else:
                    for j in range(len(temp_urls)):
                        self.blog_urls[temp_titles[j]] = temp_urls[j]
                if not content.__contains__("下一页"):
                    break
                i += 1

            except BaseException:
                logging.error("failed in getting blog list")
                break

    def get_blog_content(self):
        self.get_blog_link()
        if self.blog_urls:
            for blog_name in self.blog_urls.keys():
                url_handler = urllib2.urlopen(self.blog_urls[blog_name])
                content = url_handler.read()
                url_handler.close()
                # get blog post time like 2014-08-07 15:20
                temp_start = ( content.find('<span id="post-date">') + len('<span id="post-date">') )
                temp_end = content.find('</span>',temp_start)
                this_post_time = content[temp_start:temp_end]
                this_post_time = time.mktime(time.strptime(this_post_time, "%Y-%m-%d %H:%M"))
                # get blog content
                this_content_getter = blog_content_getter()
                this_content_getter.feed(content)
                # get blog tags


                if this_content_getter.blog_content and this_post_time:
                    self.blog_contents[blog_name] = this_content_getter.blog_content
                    self.blog_post_time[blog_name] = this_post_time


def time_converter():
    pass


if __name__ == "__main__":

    # test tag getter

    ###########
    xx = cnblog_getter()
    xx.get_blog_content()
    print len(xx.blog_contents.keys())
    #print xx.blog_contents
    for i in xx.blog_contents.keys():
        if i.__contains__("Perl"):
            print xx.blog_contents[i]
    """
    for k in xx.blog_contents:
        form_data = {
            "user_id":'00140408322081006c255e61b634c5a8937be2afc6119f7000',  # TODO
            "user_name":'Test',
            "user_image":'about:blank',
            "name": k,
            "summary":xx.blog_contents[k][:100],
            "content":xx.blog_contents[k],
        }
        form_data_urlencode = urllib.urlencode(form_data)
        req_url = "http://localhost:8000/api/addblog/"
        req = urllib2.Request(url=req_url, data=form_data_urlencode)
        print req
    """


    from www.models import Blog
    import re

    for k in xx.blog_contents.keys():
        blog = Blog(
            user_id='00140408322081006c255e61b634c5a8937be2afc6119f7000',  # TODO
            user_name='Test',
            user_image='about:blank',
            name=k,
            summary=re.sub(r"<.*?>","",xx.blog_contents[k])[0:100],
            content=xx.blog_contents[k],
            created_at=xx.blog_post_time[k],
            )
        blog.insert()
