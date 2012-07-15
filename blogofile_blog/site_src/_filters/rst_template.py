# -*- coding: utf-8 -*-
import docutils.core

from blogofile.cache import HierarchicalCache as HC

meta = {
    'name': "reStructuredText",
    'description': "Renders reStructuredText formatted text to HTML",
    }

config = HC(
    aliases = ['rst']
    )



def run(content):
    return docutils.core.publish_parts(content, writer_name='html')['html_body']
