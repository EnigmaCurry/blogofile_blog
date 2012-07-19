# -*- coding: utf-8 -*-
##############################################################################
## Archives controller
##
## Writes out yearly, monthly, and daily archives.
## Each archive is navigable to the next and previous archive
## in which posts were made.
##############################################################################

import operator
from blogofile.cache import bf
from . import (
    chronological,
    blog,
    tools,
)


def run():
    write_monthly_archives()
    write_index()


def sort_into_archives():
    #This is run in 0.initial.py
    for post in blog.iter_posts_published():
        link = post.date.strftime("archive/%Y/%m")
        try:
            blog.archived_posts[link].append(post)
        except KeyError:
            blog.archived_posts[link] = [post]
    for archive, posts in sorted(
        list(blog.archived_posts.items()), key=operator.itemgetter(0),
        reverse=True):
        name = posts[0].date.strftime("%B %Y")
        blog.archive_links.append((archive, name, len(posts)))


def write_monthly_archives():
    for link, posts in list(blog.archived_posts.items()):
        chronological.write_blog_chron(posts, root=link)


def write_index():
    month_posts = list(
        map(operator.itemgetter(1),
            sorted(blog.archived_posts.items(), reverse=True)))
    env = {"month_posts": month_posts}
    tools.materialize_template("archive_index.mako", bf.util.path_join(
            blog.path, "archive/index.html"), env)
