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
import six


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
            with patch.object(post.datetime, 'datetime') as mock_dt:
                mock_dt.now.return_value = datetime(2012, 11, 11, 8, 6, 42)
                post.config.date_format = '%Y-%m-%d %H:%M:%S'
                self._call_fut('Test Post')
        self.assertIn('date: 2012-11-11 08:06:42', mock_file.getvalue())
