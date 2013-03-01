# -*- coding: utf-8 -*-
"""Write all the blog posts in reverse chronological order.
"""
from blogofile.cache import bf
from . import (
    blog,
    tools,
)


def run():
    posts = list(blog.iter_posts_published())
    write_blog_chron(posts=posts, root=blog.pagination_dir.lstrip("/"))
    write_blog_first_page(posts)


def write_blog_chron(posts, root):
    """Write the pages, num_per_page posts per page.
    """
    page_num = 1
    post_num = 0
    while len(posts) > post_num:
        page_posts = posts[post_num:post_num + blog.posts_per_page]
        post_num += blog.posts_per_page
        if page_num > 1:
            prev_link = "../" + str(page_num - 1)
        else:
            prev_link = None
        if len(posts) > post_num:
            next_link = "../" + str(page_num + 1)
        else:
            next_link = None
        page_dir = bf.util.path_join(blog.path, root, str(page_num))
        fn = bf.util.path_join(page_dir, "index.html")
        env = {
            "posts": page_posts,
            "next_link": next_link,
            "prev_link": prev_link,
            "page_num": page_num
        }
        tools.materialize_template("chronological.mako", fn, env)
        page_num += 1


def write_blog_first_page(posts):
    if not blog.custom_index:
        page_posts = posts[:blog.posts_per_page]
        path = bf.util.path_join(blog.path, "index.html")
        blog.logger.info("Writing blog index page: " + path)
        if len(blog.posts) > blog.posts_per_page:
            next_link = bf.util.site_path_helper(
                    blog.path, blog.pagination_dir + "/2")
        else:
            next_link = None
        env = {
            "posts": page_posts,
            "next_link": next_link,
            "prev_link": None
        }
        tools.materialize_template("chronological.mako", path, env)
