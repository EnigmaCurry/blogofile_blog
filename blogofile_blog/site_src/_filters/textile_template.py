# -*- coding: utf-8 -*-
import textile

from blogofile.cache import HierarchicalCache as HC

meta = {
    'name': "Textile",
    'description': "Renders textile formatted text to HTML",
    }

config = HC(
    aliases = ['textile']
    )

def run(content):
    return textile.textile(content)
