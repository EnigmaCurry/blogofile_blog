# -*- coding: utf-8 -*-
"""Unit tests for blogofile blog post module.
"""
from datetime import datetime
try:
    import unittest2 as unittest        # For Python 2.6
except ImportError:
    import unittest                     # flake8 ignore # NOQA
from mock import (
    mock_open,
    patch,
    )
import pytz
import six


class TestCreateGuid(unittest.TestCase):
    """Unit tests for create_guid function."""
    def _get_fut(self):
        from blog.post import create_guid
        return create_guid

    def _call_fut(self, *args, **kwargs):
        return self._get_fut()(*args, **kwargs)

    def test_create_guid(self):
        """create_guid returns expected string
        """
        guid = self._call_fut(six.u('Je suis arrivé'), datetime(2012, 12, 1))
        try:
            # Python 3 result
            self.assertEqual(guid, six.u('84mH0fap8NAz8GuFxu7aBXNn4pw='))
        except AssertionError:
            # Python 2 result
            self.assertEqual(guid, six.u('sCCVan827mZtY6wRvRKGJ9x1L44='))


class TestCreatePermalink(unittest.TestCase):
    """Unit tests for create_permalink function."""
    def _get_fut(self):
        from blog.post import create_permalink
        return create_permalink

    def _call_fut(self, *args, **kwargs):
        return self._get_fut()(*args, **kwargs)

    def test_create_permalink_year_month_title(self):
        """create_permalink has expected result for :year/:month/:title
        """
        kwargs = {
            'site_url': 'http://www.example.com',
            'blog_path': '/blog',
            'title': 'Test Title',
            'date': datetime(2012, 12, 1),
            'uuid': '123456789-aaaa-12345',
            'filename': '001-post-one.markdown',
            }
        permalink = self._call_fut(':blog_path/:year/:month/:title', **kwargs)
        self.assertEqual(
            permalink,
            'http://www.example.com/blog/2012/12/test-title')

    def test_create_permalink_uuid_str_filename(self):
        """create_permalink has expected result for :uuid/fuxx/:filename
        """
        kwargs = {
            'site_url': 'http://www.example.com',
            'blog_path': '/blog',
            'title': 'Test Title',
            'date': datetime(2012, 12, 1),
            'uuid': '123456789-aaaa-12345',
            'filename': '001-post-one.markdown',
            }
        permalink = self._call_fut('/:uuid/fuzz/:filename', **kwargs)
        self.assertEqual(
            permalink,
            'http://www.example.com/123456789-aaaa-12345/fuzz/'
            '001-post-one-markdown')


class TestCreatePostTemplate(unittest.TestCase):
    """Unit tests for create_post_template function."""
    def _get_fut(self):
        from blog.post import create_post_template
        return create_post_template

    def _call_fut(self, *args, **kwargs):
        return self._get_fut()(*args, **kwargs)

    def test_create_post_tmpl_date_time_format_from_config(self):
        """date in post header uses config.blog.post.date_format
        """
        from blog import post
        mo = mock_open()
        # nested contexts for Python 2.6 compatibility
        with patch.object(post, 'open', mo, create=True):
            mock_file = six.StringIO()
            mo().__enter__.return_value = mock_file
            with patch.object(post, 'datetime') as mock_dt:
                mock_dt.now.return_value = datetime(2012, 11, 11, 8, 6, 42)
                self.addCleanup(
                    setattr, post.config, 'date_format',
                    post.config.date_format)
                post.config.date_format = '%Y-%m-%d %H:%M:%S'
                self._call_fut('Test Post')
        self.assertIn('date: 2012-11-11 08:06:42', mock_file.getvalue())


class TestPost(unittest.TestCase):
    """Unit tests for Post class."""
    def _get_target_class(self):
        from blog.post import Post
        return Post

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_parse_yaml_sets_default_date_if_missing(self):
        """header date set to datetime.now if it is missing
        """
        from blog import post
        from blog.post import blog_config
        post_content = (
            '---\n'
            'title: Test Post\n'
            '---\n'
            )
        with patch.object(post, 'datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2012, 11, 12, 10, 51, 42)
            post = self._make_one(post_content)
        expected = pytz.timezone(blog_config.timezone).localize(
            datetime(2012, 11, 12, 10, 51, 42))
        self.assertEqual(post.date, expected)

    def test_parse_yaml_date_w_date_format(self):
        """header date is converted from string using post.config.date_format
        """
        from blog.post import blog_config
        post_content = (
            '---\n'
            'title: Test Post\n'
            'date: 2012/11/11 19:33:42\n'
            '---\n'
            )
        post = self._make_one(post_content)
        expected = pytz.timezone(blog_config.timezone).localize(
            datetime(2012, 11, 11, 19, 33, 42))
        self.assertEqual(post.date, expected)

    def test_parse_yaml_date_w_datetime(self):
        """header date converted to datetime by YAML parser handled correctly
        """
        from blog.post import blog_config
        post_content = (
            '---\n'
            'title: Test Post\n'
            'date: 2012-11-11 19:33:42\n'
            '---\n'
            )
        self.addCleanup(
            setattr, blog_config.post, 'date_format',
            blog_config.post.date_format)
        blog_config.post.date_format = '%Y-%m-%d %H:%M:%S'
        post = self._make_one(post_content)
        expected = pytz.timezone(blog_config.timezone).localize(
            datetime(2012, 11, 11, 19, 33, 42))
        self.assertEqual(post.date, expected)

    def test_parse_yaml_sets_default_updated_if_missing(self):
        """header updated set to header date if it is missing
        """
        post_content = (
            '---\n'
            'title: Test Post\n'
            'date: 2012/11/12 11:05:42\n'
            '---\n'
            )
        post = self._make_one(post_content)
        self.assertEqual(post.updated, post.date)

    def test_parse_yaml_updated_w_date_format(self):
        """header updated is converted from string w/ post.config.date_format
        """
        from blog.post import blog_config
        post_content = (
            '---\n'
            'title: Test Post\n'
            'date: 2012/11/11 19:33:42\n'
            'updated: 2012/11/11 20:58:42\n'
            '---\n'
            )
        post = self._make_one(post_content)
        expected = pytz.timezone(blog_config.timezone).localize(
            datetime(2012, 11, 11, 20, 58, 42))
        self.assertEqual(post.updated, expected)

    def test_parse_yaml_updated_w_datetime(self):
        """header updated converted to updatedtime by YAML parser handled ok
        """
        from blog.post import blog_config
        post_content = (
            '---\n'
            'title: Test Post\n'
            'date: 2012-11-11 19:33:42\n'
            'updated: 2012-11-11 20:58:42\n'
            '---\n'
            )
        self.addCleanup(
            setattr, blog_config.post, 'date_format',
            blog_config.post.date_format)
        blog_config.post.date_format = '%Y-%m-%d %H:%M:%S'
        post = self._make_one(post_content)
        expected = pytz.timezone(blog_config.timezone).localize(
            datetime(2012, 11, 11, 20, 58, 42))
        self.assertEqual(post.updated, expected)
