#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.parse
import re
import blogofile
import blogofile.plugin
from blogofile.cache import bf, HierarchicalCache as HC


from . import commands

## Configure the plugin meta information:
__dist__ = dict(
    #The name of your plugin:
    name = "Blog",
    #The namespace of your plugin as used in _config.py.
    #referenced as bf.config.plugins.name
    config_name = "blog",
    #Your name:
    author = "Ryan McGuire",
    #The version number:
    version = "0.8",
    #The URL for the plugin (where to download, documentation etc):
    url = "http://www.blogofile.com",
    #A one line description of your plugin presented to other Blogofile users:
    description = "A simple blog engine",
    #PyPI description, could be the same, except this text
    #should mention the fact that this is a Blogofile plugin
    #because non-Blogofile users will see this text:
    pypi_description = "A simple blog engine plugin for Blogofile",
    #Command parser
    command_parser_setup = commands.setup_parser
    )

__version__ = __dist__["version"]

config = HC(
    # name -- Your Blog's name.
    # This is used repeatedly in default blog templates
    name = "Your Blog's name",
    ## blog_description -- A short one line description of the blog
    # used in the RSS/Atom feeds.
    description = "Your Blog's short description",
    ## blog_path -- Blog path.
    #  This is the path of the blog relative to the site_url.
    #  If your site_url is "http://www.yoursite.com/~ryan"
    #  and you set blog_path to "/blog" your full blog URL would be
    #  "http://www.yoursite.com/~ryan/blog"
    #  Leave blank "" to set to the root of site_url
    path = "/blog",
    ## blog_timezone -- the timezone that you normally write your blog posts from
    timezone = "US/Eastern",
    ## blog_posts_per_page -- Blog posts per page
    posts_per_page = 5,
    # Automatic Permalink
    # (If permalink is not defined in post article, it's generated
    #  automatically based on the following format:)
    # Available string replacements:
    # :year, :month, :day -> post's date
    # :title              -> post's title
    # :uuid               -> sha hash based on title
    # :filename           -> article's filename without suffix
    # path is relative to site_url
    auto_permalink = HC(enabled=True,
                         path=":blog_path/:year/:month/:day/:title"),
    # Automatic Post filenames
    # Post can be created automatically with:
    #   blogofile blog post create "Post Title"
    # auto_post_filename defines the filename format for posts
    # created this way.
    auto_post_filename = ":year-:month-:day - :title.markdown",
    #### Disqus.com comment integration ####
    disqus = HC(enabled=False,
                 name="your_disqus_name"),
    #### Custom blog index ####
    # If you want to create your own index page at your blog root
    # turn this on. Otherwise blogofile assumes you want the
    # first X posts displayed instead
    custom_index = False,
    #### Post excerpts ####
    # If you want to generate excerpts of your posts in addition to the
    # full post content turn this feature on
    #Also, if you don't like the way the post excerpt is generated
    #You can define assign a new function to blog.post_excerpts.method
    #This method must accept the following arguments: (content, num_words)
    post_excerpts = HC(enabled=True,
                        word_length=25),
    #### Blog pagination directory ####
    # blogofile places extra pages of your blog in
    # a secondary directory like the following:
        # http://www.yourblog.com/blog_root/page/4
    # You can rename the "page" part here:
    pagination_dir = "page",
    #### Blog category directory ####
    # blogofile places extra pages of your or categories in
    # a secondary directory like the following:
    # http://www.yourblog.com/blog_root/category/your-topic/4
    # You can rename the "category" part here:
    category_dir = "category",
    priority = 90.0,
    base_template = "site.mako",
    #Alternative template engine content blocks:
    template_engines = HC(
        jinja2 = HC(
            content_regex = re.compile("{%\W*block content\W*%}.*?{%\W*endblock\W*%}", re.MULTILINE|re.DOTALL )
            )
        ),
    #Where to find the templates? Can be relocated to user-space.
    template_path = None,
    #Posts
    post = HC(
        date_format = "%Y/%m/%d %H:%M:%S",
        encoding = "utf-8",
        #What files in _posts directory should we consider posts?
        file_regex = ".*((\.textile$)|(\.markdown$)|(\.md$)|"\
            "(\.org$)|(\.html$)|(\.txt$)|(\.rst$))",
        #### Default post filters ####
        # If a post does not specify a filter chain, use the
        # following defaults based on the post file extension:
        default_filters = {
           "markdown": "syntax_highlight, markdown",
           "textile": "syntax_highlight, textile",
           "org": "syntax_highlight, org",
           "rst": "syntax_highlight, rst",
           "html": "syntax_highlight"
           },
        #An optional callback to run after all the posts are parsed
        #but before anything else is done with them.
        post_process = None,
        #Default Slugification function uses post titles.  User may
        #redefine their own function here, single argument is the Post
        #object:
        slugify = None,
        categories = HC(
            case_sensitive = False
            )
        )
    )

tools = blogofile.plugin.PluginTools(__name__)

def init():
    tools.initialize_controllers()

