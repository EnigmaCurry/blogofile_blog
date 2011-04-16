"""
post.py parses post sources from the ./_post directory.
"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"

import os
import sys
import datetime
import re
import operator
import urllib.parse
import hashlib
import codecs
import base64
import urllib.request
import urllib.parse
import urllib.error
from xml.sax import saxutils

import pytz
import yaml
import logging

from blogofile import util
import blogofile_bf as bf

logger = logging.getLogger("blogofile.post")
from . import config as blog_config

config = blog_config.post
config.mod = sys.modules[__name__]

# These are all the Blogofile reserved field names for posts. It is not
# recommended that users re-use any of these field names for purposes other
# than the one stated.
reserved_field_names = {
    "title"      :"A one-line free-form title for the post",
    "date"       :"The date that the post was originally created",
    "updated"    :"The date that the post was last updated",
    "categories" :"A list of categories that the post pertains to, "\
        "each seperated by commas",
    "tags"       :"A list of tags that the post pertains to, "\
        "each seperated by commas",
    "permalink"  :"The full permanent URL for this post. "\
        "Automatically created if not provided",
    "path"       :"The path from the permalink of the post",
    "guid"       :"A unique hash for the post, if not provided it "\
        "is assumed that the permalink is the guid",
    "slug"       :"The title part of the URL for the post, if not "\
        "provided it is automatically generated from the title."\
        "It is not used if permalink does not contain :title",
    "author"     :"The name of the author of the post",
    "filters"    :"The filter chain to apply to the entire post. "\
        "If not specified, a default chain based on the file extension is "\
        "applied. If set to 'None' it disables all filters, even default ones.",
    "filter"     :"synonym for filters",
    "draft"      :"If 'true' or 'True', the post is considered to be only a "\
        "draft and not to be published.",
    "source"     :"Reserved internally",
    "yaml"       :"Reserved internally",
    "content"    :"Reserved internally",
    "filename"   :"Reserved internally",
    "encoding"   :"The file encoding format"
    }


class PostParseException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Post(object):
    """
    Class to describe a blog post and associated metadata
    """
    def __init__(self, source, filename="Untitled"):
        self.source = source
        self.yaml = None
        self.title = None
        self.__timezone = blog_config.timezone
        self.date = None
        self.updated = None
        self.categories = set()
        self.tags = set()
        self.permalink = None
        self.content = ""
        self.excerpt = ""
        self.filename = filename
        self.author = ""
        self.guid = None
        self.slug = None
        self.draft = False
        self.filters = None
        self.__parse()
        self.__post_process()
        
    def __repr__(self): #pragma: no cover
        return "<Post title='{0}' date='{1}'>".format(
            self.title, self.date.strftime("%Y/%m/%d %H:%M:%S"))
     
    def __parse(self):
        """Parse the yaml and fill fields"""
        yaml_sep = re.compile("^---$", re.MULTILINE)
        content_parts = yaml_sep.split(self.source, maxsplit=2)
        if len(content_parts) < 2:
            raise PostParseException("Post has no YAML section: {0}".format(
                    self.filename))
        else:
            #Extract the yaml at the top
            self.__parse_yaml(content_parts[1])
            post_src = content_parts[2]
        self.__apply_filters(post_src)
        #Do post excerpting
        self.__parse_post_excerpting()

    def __apply_filters(self, post_src):
        """Apply filters to the post"""
        #Apply block level filters (filters on only part of the post)
        # TODO: block level filters on posts
        #Apply post level filters (filters on the entire post)
        #If filter is unspecified, use the default filter based on
        #the file extension:
        if self.filters is None:
            try:
                file_extension = os.path.splitext(self.filename)[-1][1:]
                self.filters = blog_config.post.default_filters[
                    file_extension]
            except KeyError:
                self.filters = []
        self.content = bf.filter.run_chain(self.filters, post_src)
        
    def __parse_post_excerpting(self):
        if blog_config.post_excerpts.enabled:
            length = blog_config.post_excerpts.word_length
            try:
                self.excerpt = bf.config.post_excerpt(self.content, length)
            except AttributeError:
                self.excerpt = self.__excerpt(length)

    def __excerpt(self, num_words=50):
        #Default post excerpting function
        #Can be overridden in _config.py by
        #defining post_excerpt(content,num_words)
        # if len(self.excerpt) == 0:
        #      """Retrieve excerpt from article"""
        #      s = BeautifulSoup.BeautifulSoup(self.content)
        #      # get rid of javascript, noscript and css
        #      [[tree.extract() for tree in s(elem)] for elem in (
        #              'script', 'noscript', 'style')]
        #      # get rid of doctype
        #      subtree = s.findAll(text=re.compile("DOCTYPE|xml"))
        #      [tree.extract() for tree in subtree]
        #      # remove headers
        #      [[tree.extract() for tree in s(elem)] for elem in (
        #              'h1', 'h2', 'h3', 'h4', 'h5', 'h6')]
        #      text = ''.join(s.findAll(text=True))\
        #                          .replace("\n", "").split(" ")
        #      return " ".join(text[:num_words]) + '...'
        return self.content
        
    def __post_process(self):
        # fill in empty default value
        if not self.date:
            self.date = datetime.datetime.now(pytz.timezone(self.__timezone))
        if not self.updated:
            self.updated = self.date
            
        #Make sure dates have timezone info:
        if not self.date.tzinfo:
            pytz.timezone(self.__timezone).localize(self.date)
        if not self.updated.tzinfo:
            pytz.timezone(self.__timezone).localize(self.updated)

        if not self.title:
            self.title = "Untitled - {0}".format(self.date)
        if not self.slug:
            if config.slugify:
                #The use has provided their own slugify function, use that:
                self.slug = config.slugify(self)
            else:
                self.slug = create_slug(self.title)
            
        if not self.categories or len(self.categories) == 0:
            self.categories = set([Category('uncategorized')])
        if self.guid:
            uuid = urllib.parse.quote(self.guid) #used for expandling :uuid in permalink template code below
        else:
            self.guid = uuid = create_guid(self.title, self.date)
        if not self.permalink and \
                blog_config.auto_permalink.enabled:
            self.permalink = create_permalink(
                blog_config.auto_permalink.path, bf.config.site.url,
                blog_config.path, self.title, self.date, uuid, self.filename)
        
        logger.debug("Permalink: {0}".format(self.permalink))
     
    def __parse_yaml(self, yaml_src):
        try:
            y = yaml.load(yaml_src)
        except yaml.YAMLError as e:
            linenum = 1
            if getattr(e, 'context_mark', None):
                linenum = 1 + e.context_mark.line
            raise PostParseException(
                "Post has bad YAML section: {0}:{1}".format(
                    self.filename, linenum, str(e)))
        if not isinstance(y, dict):
            raise PostParseException(
                "Post has bad YAML section: {0}".format(self.filename))
        # Load all the fields that require special processing first:
        fields_need_processing = ('permalink', 'guid', 'date', 'updated',
                                  'categories', 'tags', 'draft')
        try:
            self.permalink = y['permalink']
            if self.permalink.startswith("/"):
                self.permalink = urllib.parse.urljoin(bf.config.site.url,
                        self.permalink)
            #Ensure that the permalink is for the same site as bf.config.site.url
            if not self.permalink.startswith(bf.config.site.url):
                raise PostParseException("{0}: permalink for a different site"
                        " than configured".format(self.filename))
            logger.debug("path from permalink: {0}".format(self.path))
        except KeyError:
            pass
        try:
            self.guid = y['guid']
        except KeyError:
            self.guid = self.permalink
        try:
            self.date = pytz.timezone(self.__timezone).localize(
                datetime.datetime.strptime(y['date'], config.date_format))
        except KeyError:
            pass
        try:
            self.updated = pytz.timezone(self.__timezone).localize(
                datetime.datetime.strptime(y['updated'], config.date_format))
        except KeyError:
            pass
        try:
            if config.categories.case_sensitive:
                self.categories = set([Category(x.strip()) for x in \
                                           y['categories'].split(",")])
            else:
                self.categories = set([Category(x.strip().lower()) for x in \
                                           y['categories'].split(",")])
        except:
            pass
        try:
            self.tags = set([x.strip() for x in y['tags'].split(",")])
        except:
            pass
        try:
            self.filters = y['filter'] #filter is a synonym for filters
        except KeyError:
            pass
        try:
            if y['draft']:
                self.draft = True
                logger.info("Ignoring Draft Post: {0}".format(self.filename))
            else:
                self.draft = False
        except KeyError:
            self.draft = False
        # Load the rest of the fields that don't need processing:
        for field, value in list(y.items()):
            if field not in fields_need_processing:
                setattr(self,field,value)
        
    def permapath(self):
        """Get just the path portion of a permalink"""
        return urllib.parse.urlparse(self.permalink)[2]

    def __cmp__(self, other_post):
        "Posts should be comparable by date"
        return cmp(self.date, other_post.date)

    def __eq__(self, other_post):
        return self is other_post

    def __getattr__(self, name):
        if name == "path":
            #Always generate the path from the permalink
            return self.permapath()
        else:
            raise AttributeError(name)


class Category(object):

    def __init__(self, name):
        self.name = str(name)
        # TODO: slugification should be abstracted out somewhere reusable
        # TODO: consider making url_name and path read-only properties?
        self.url_name = self.name.lower().replace(" ", "-")
        self.path = bf.util.site_path_helper(
                blog_config.path,
                blog_config.category_dir,
                self.url_name)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name
    
    def __lt__(self, other):
        return self.name < other.name
    def __eq__(self, other):
        return not self<other and not other<self
    def __ne__(self, other):
      return self<other or other<self
    def __gt__(self, other):
        return other<self
    def __ge__(self, other):
        return not self<other
    def __le__(self, other):
        return not other<self
    
def create_guid(title, date):
    #This tricky bit is not handled well with 2to3, so we have to hand
    #craft the python2 translation:
    if sys.version_info >= (3,):
        to_hash = eval("bytes(date.isoformat() + title,\"utf-8\")")
    else:
        to_hash = eval("date.isoformat() + title.encode(\"utf-8\")")
    return base64.urlsafe_b64encode(hashlib.sha1(to_hash).digest())

def create_slug(title):
    #Get rid of any html entities
    slug = saxutils.unescape(title)
    #Remove any non-valid URL characters (reference RFC 1738 section 2.2)
    slug = re.sub("[^a-zA-Z0-9$\-_\.+!*'(),]", "-", slug).lower()
    return slug

def create_permalink(auto_permalink_path, site_url,
                     blog_path, title, date, uuid, filename):
    """
    >>> d = {"site_url" : "http://www.example.com",\
         "blog_path" : "/blog",\
         "title" : "Test Title",\
         "date" : datetime.datetime(2011, 2, 28),\
         "uuid" : "123456789-aaaa-12345",\
         "filename" : "001-post-one.markdown" }
    >>> create_permalink(":blog_path/:year/:month/:title",**d)
    'http://www.example.com/blog/2011/02/test-title'
    >>> create_permalink("/:uuid/fuzz/:filename",**d)
    'http://www.example.com/123456789-aaaa-12345/fuzz/001-post-one.markdown'
    """
    permalink = site_url.rstrip("/") + auto_permalink_path
    permalink = \
        re.sub(":blog_path", blog_path, permalink)
    permalink = \
        re.sub(":year", date.strftime("%Y"), permalink)
    permalink = \
        re.sub(":month", date.strftime("%m"), permalink)
    permalink = \
        re.sub(":day", date.strftime("%d"), permalink)
    permalink = \
        re.sub(":hour", date.strftime("%H"), permalink)
    permalink = \
        re.sub(":minute", date.strftime("%M"), permalink)
    permalink = \
        re.sub(":second", date.strftime("%S"), permalink)
    permalink = \
        re.sub(":title", create_slug(title), permalink)
    permalink = \
        re.sub(":filename", create_slug(filename), permalink)
    permalink = re.sub(":uuid", uuid, permalink)
    return permalink

def parse_posts(directory):
    """Retrieve all the posts from the directory specified.

    Returns a list of the posts sorted in reverse by date."""
    posts = []
    post_filename_re = re.compile(config.file_regex)
    if not os.path.isdir("_posts"):
        logger.warn("This site has no _posts directory.")
        return []
    post_paths = [f for f in bf.util.recursive_file_list(
            directory, post_filename_re) if post_filename_re.match(f)]

    for post_path in post_paths:
        post_fn = os.path.split(post_path)[1]
        logger.debug("Parsing post: {0}".format(post_path))
        #IMO codecs.open is broken on Win32.
        #It refuses to open files without replacing newlines with CR+LF
        #reverting to regular open and decode:
        try:
            src = open(post_path, "r").read()
        except:
            logger.exception("Error reading post: {0}".format(post_path))
            raise
        try:
            p = Post(src, filename=post_fn)
        except PostParseException as e:
            logger.warning("{0} : Skipping this post.".format(e.value))
            continue
        posts.append(p)
    posts.sort(key=operator.attrgetter('date'), reverse=True)
    return posts

def create_post_filename(spec, title, date):
    filename = spec
    filename = re.sub(":title", create_slug(title), filename)
    filename = re.sub(":year", date.strftime("%Y"), filename)
    filename = re.sub(":month", date.strftime("%m"), filename)
    filename = re.sub(":day", date.strftime("%d"), filename)
    filename = re.sub(":hour", date.strftime("%H"), filename)
    filename = re.sub(":minute", date.strftime("%M"), filename)
    filename = re.sub(":second", date.strftime("%S"), filename)
    return filename

def create_post_template(title,**params):
    params['title'] = title
    if "date" in params:
        date = params['date']
    else:
        date = params['date'] = datetime.datetime.now()
    if "uuid" not in params:
        params['uuid'] = create_guid(title, date)
    if "filename" not in params:
        params['filename'] = ""
    if "permalink" not in params:
        params['permalink'] = create_permalink(
            blog_config.auto_permalink.path, bf.config.site.url,
            blog_config.path, **params)
    params['date'] = date.strftime("%Y/%m/%d %H:%M:%S")
    params['categories'] = ""
    template = """---
title: {title}
permalink: {permalink}
date: {date}
categories: {categories}
guid: {uuid}
---
""".format(**params)
    if not os.path.isdir("_posts"):
        util.mkdir("_posts")
    post_filename = os.path.join("_posts",create_post_filename(
                ":year-:month-:day - :title.markdown", title, date))
    if os.path.exists(post_filename):
        logger.error("A file already exists called {0}, I won't overwrite it.".format(post_filename))
        return
    with open(post_filename,"w") as f:
        f.write(template)
        
