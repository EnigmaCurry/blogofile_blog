This is a Blogofile_ plugin that implements a basic blog engine.

.. _Blogofile: http://www.blogofile.com/

It provides a collection of Mako template files along with CSS and ancillary
files,
all derived from the HTML5Boilerplate project.
It also provided Blogofile_ configuration, controllers, filters, and commands
to allow you to create a simple blog engine that requires no database
and no special hosting environment.

The templates include features like:

* Custom `web fonts from Google`_
* Disqus_ comments
* `Google Analytics`_ tracking code stub
* seaofclouds_ jQuery twitter plugin

.. _web fonts from Google: http://www.google.com/webfonts/
.. _Disqus: http://disqus.com/
.. _Google Analytics: http://www.google.com/analytics/
.. _seaofclouds: http://tweet.seaofclouds.com/

Use them or remove them as you wish.

There's also a few sample posts to show off:

* Syntax highlighting for code snippets
* Unicode support
* Basic Markdown syntax

Customize the Mako templates,
create posts in reStructuredText, Markdown, or Textile, (or even plain HTML)
and blogofile generates your entire blog as
plain HTML, CSS, Javascript, images, and Atom/RSS feeds
which you can then upload to any old web server you like.
No database.
No CGI or scripting environment on the server.
Just fast, secure static content!

Take a look at the blogofile `project docs`_ for a quick-start guide,
and detailed usage instructions.

Or create a virtualenv and dive right in with::

  pip install -U blogofile
  pip install -U blogofile_blog

.. _project docs: http://blogofile.readthedocs.org/en/latest/
