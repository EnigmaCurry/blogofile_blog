# -*- coding: utf-8 -*-
"""Integration tests for blogofile_blog plugin.
"""
import os
import shutil
from tempfile import mkdtemp
try:
    import unittest2 as unittest        # For Python 2.6
except ImportError:
    import unittest                     # flake8 ignore # NOQA
from blogofile import main


class TestBlogofileBlogCommands(unittest.TestCase):
    """Intrgration tests for the blogofile_blog commands.
    """
    def _call_entry_point(self, *args):
        main.main(*args)

    def test_blogofile_init_blog_site(self):
        """`blogofile init src blog` initializes blog site w/ expected files
        """
        src_dir = mkdtemp()
        self.addCleanup(shutil.rmtree, src_dir)
        os.rmdir(src_dir)
        self._call_entry_point(['blogofile', 'init', src_dir, 'blog'])
        self.assertEqual(
            set(os.listdir(src_dir)),
            set('_config.py 404.html _htaccess _posts _templates '
                'crossdomain.xml css favicon.ico img index.html.mako js '
                'robots.txt themes'
                .split()))

    def test_blogofile_build_blog_site(self):
        """`blogofile build` on blog site creates _site directory
        """
        self.addCleanup(os.chdir, os.getcwd())
        src_dir = mkdtemp()
        self.addCleanup(shutil.rmtree, src_dir)
        os.rmdir(src_dir)
        self._call_entry_point(['blogofile', 'init', src_dir, 'blog'])
        self._call_entry_point(['blogofile', 'build', '-s', src_dir])
        self.assertIn('_site', os.listdir(src_dir))
