#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urlparse
import blogofile
from blogofile.cache import bf, HierarchicalCache as HC

## Configure the plugin meta information:
__dist__ = dict(
    #The name of your plugin:
    name = "Blog",
    #The namespace of your plugin as used in _config.py.
    #referenced as bf.config.plugins.name
    config_name = "blog",
    #Your name:
    author = "Ryan McGuire",
    #The version number:
    version = "0.8",
    #The URL for the plugin (where to download, documentation etc):
    url = "http://www.blogofile.com",
    #The description of your plugin presented to other Blogofile users:
    description = "A simple blog engine",
    #PyPI description, could be the same, except this text
    #should mention the fact that this is a Blogofile plugin
    #because non-Blogofile users will see this text:
    pypi_description = "A simple blog engine plugin for Blogofile"
    )

__version__ = __dist__["version"]

config = HC()

tools = blogofile.plugin.PluginTools(__name__)

def init():
    tools.initialize_controllers()

def run():
    tools.run_controllers()
