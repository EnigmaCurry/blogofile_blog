# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import shutil
import sys
import os, os.path
import imp

import blogofile.main


def load_env():
    global tools, post
    from . import tools
    sys.path.insert(0,os.path.join(tools.get_src_dir(),"_controllers"))
    from blog import post
    sys.path.pop(0)
    
def setup_parser(parent_parser, parser_template):
    from . import __dist__
    #Add additional subcommands under the blog parser:
    blog_subparsers = parent_parser.add_subparsers()

    #Blog templates
    blog_templates = blog_subparsers.add_parser(
        "templates", help="Blog template helpers", parents=[parser_template])
    blog_templates_subparsers = blog_templates.add_subparsers()
    blog_templates_copy = blog_templates_subparsers.add_parser(
        "copy", help="Copy blog templates to DEST", parents=[parser_template])
    blog_templates_copy.add_argument("DEST", help="Destiation to copy templates to")
    blog_templates_copy.set_defaults(func=copy_templates)

    #Blog posts
    blog_post = blog_subparsers.add_parser(
        "post", help="Blog post helpers", parents=[parser_template])
    blog_post_subparsers = blog_post.add_subparsers()
    blog_post_create = blog_post_subparsers.add_parser(
        "create", help="Create a new blog post", parents=[parser_template])
    blog_post_create.add_argument("TITLE", help="Title of new blog post")
    blog_post_create.set_defaults(func=create_post)
    blog_post_list = blog_post_subparsers.add_parser(
        "list", help="List blog posts", parents=[parser_template])
    blog_post_list.set_defaults(func=list_posts)

def copy_templates(args):
    """Copy the blog templates to the given directory"""
    load_env()
    try:
        shutil.copytree(os.path.join(tools.get_src_dir(),"_templates","blog"),args.DEST)
    except OSError:
        print(("Destination ({0}) already exists.\nYou must choose a path that does not yet exist.".format(args.DEST)))
        return
    print(("\nCopied blog templates to : {0}".format(args.DEST)))
    print("To use them, edit your _config.py:")
    print(("\n   plugins.blog.template_path = \"{0}\"\n".format(os.path.relpath(args.DEST,os.curdir))))
    
def create_post(args):
    blogofile.config.init_interactive(args)
    load_env()
    post.create_post_template(args.TITLE)

def list_posts(args):
    blogofile.config.init_interactive(args)

    from blogofile import plugin, filter
    plugin.init_plugins()
    filter.init_filters()
    
    load_env()
    posts = post.parse_posts("_posts")
    p_num = len(posts)
    for p in post.parse_posts("_posts"):
        print(("{0} | {1} | {2} | {3}".format(str(p_num).rjust(4), p.date.strftime("%Y/%m/%d"), p.title, p.filename)))
        p_num -= 1
