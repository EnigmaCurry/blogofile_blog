import re
import os
import os.path
import tempfile
import blogofile_bf as bf
from blogofile.template import MakoTemplate

from . import tools
from . import config as blog

mako_template_re = re.compile("\.mako$")
mako_content_place_holder = re.compile("~~!`MAKO_CONTENT_HERE`!~~")

def materialize_template(template_name, location, attrs={}, lookup=None):
    #Provide the base template programatically:
    tools.template_lookup.put_template(
        "blog_base_template",tools.template_lookup.get_template(
            blog.base_template))
    #If the base template is something other than mako handle it differently:
    if mako_template_re.search(blog.base_template):
        tools.materialize_template_original(template_name, location, attrs=attrs, lookup=lookup)
    else:
        materialize_alternate_base_engine(template_name, location, attrs=attrs, lookup=lookup)
        
def materialize_alternate_base_engine(template_name, location, attrs={}, lookup=None):
    # We can materialize the Mako blog templates within a base
    # template defined with an alternative template engine
    # (Jinja2,kid,etc) with the following procedure:
    
    # 1) Load the base template source, and mark the content block
    # for later replacement.
    #
    # 2) Materialize the jinja template in a temporary location with
    # attrs.
    #
    # 3) Convert the HTML to Mako with ${next.body()} where the old
    # content block was.
    #
    # 4) Materialize the blog template setting blog_base_template to
    # the new template

    #Find which template type it is:
    template_engine = None
    for extension, engine in bf.config.templates.engines.items():
        if blog.base_template.endswith(extension):
            template_engine = engine
            break
    else:
        raise Exception("Unknown engine for base template: '{0}'"\
                            .format(blog.base_template))
    base_template_src = open(bf.util.path_join("_templates",blog.base_template)).read()
    #Replace the content block with our own marker:
    base_template_src = blog.template_engines[template_engine.name].\
        content_regex.sub(mako_content_place_holder.pattern,base_template_src)
    html = str(template_engine(None, src=base_template_src).render(),"utf-8")
    html = mako_content_place_holder.sub("${next.body()}",html)
    mako_file = tempfile.mktemp(suffix=".mako",prefix="bf_template",dir=blog.temp_proc_dir)
    mako_file_name = os.path.split(mako_file)[1]
    with open(mako_file,"w") as f:
        f.write(html)
    tools.template_lookup.put_template(
        "blog_base_template",tools.template_lookup.get_template(mako_file_name))
    tools.materialize_template_original(template_name,location,attrs,lookup)
    os.remove(mako_file)

def setup():
    tools.template_lookup.directories.append(blog.temp_proc_dir)
    tools.materialize_template_original = tools.materialize_template
    tools.materialize_template = materialize_template
    
