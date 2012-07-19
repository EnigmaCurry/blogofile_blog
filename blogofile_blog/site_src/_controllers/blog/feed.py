# -*- coding: utf-8 -*-
from blogofile.cache import bf
from . import blog, tools


def run():
    posts = list(blog.iter_posts_published())
    write_feed(posts, bf.util.path_join(blog.path, "feed"), "rss.mako")
    write_feed(
        posts, bf.util.path_join(blog.path, "feed", "atom"), "atom.mako")


def write_feed(posts, root, template):
    root = root.lstrip("/")
    path = bf.util.path_join(root, "index.xml")
    blog.logger.info("Writing RSS/Atom feed: " + path)
    env = {"posts": posts, "root": root}
    tools.materialize_template(template, path, env)
