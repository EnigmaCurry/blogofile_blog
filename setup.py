# If you're looking here for an example for creating your own
# Blogofile plugins, there's a much simpler example here:
# http://github.com/EnigmaCurry/blogofile_example_plugin
# This setup.py is necessarily more complex because it has to support
# both Python 3 and 2.

from setuptools import setup, find_packages
from distutils.command.sdist import sdist
import sys
import os.path
import imp
import re
import shutil

def setup_python2():
    #Blogofile is written for Python 3.
    #But we can also experimentally support Python 2 with lib3to2.
    from lib3to2 import main as three2two
    from distutils import dir_util
    import shutil
    import shlex
    tmp_src = "src_py2"
    try:
        shutil.rmtree(tmp_src)
    except OSError:
        pass #ignore if the directory doesn't exist.
    shutil.copytree("blogofile_blog",os.path.join(tmp_src,"blogofile_blog"))
    three2two.main("lib3to2.fixes",shlex.split(
            "-w {0}".format(tmp_src)))
    return tmp_src

if sys.version_info < (3,):
    sys.path.insert(0,"src_py2")
    src_root = os.path.join("src_py2","blogofile_blog")
    import blogofile_blog
    try:
        import blogofile_blog
    except ImportError:
        print("-"*80)
        print("Python 3.x is required to develop and build Blogofile.")
        print("Python 2.x versions of Blogofile can be installed with "
              "a stable tarball\nfrom PyPI. e.g. 'easy_install blogofile_blog'\n")
        print("Alternatively, you can build your own tarball with "
              "'python3 setup.py sdist'.")
        print("This will require Python 3 and 3to2, and will produce a tarball "
              "that can be\ninstalled in either Python 2 or 3.")
        print("-"*80)
        sys.exit(1)
else:
    src_root = "blogofile_blog"
    import blogofile_blog

class sdist_py2(sdist):
    "sdist for python2 which runs 3to2 over the source before packaging"
    def run(self):
        setup_python2()
        sdist.run(self)
        shutil.rmtree("src_py2")
        
def find_package_data(module, path):
    """Find all data files to include in the package"""
    files = []
    exclude = re.compile("\.pyc$|~$")
    for dirpath, dirnames, filenames in os.walk(os.path.join(module,path)):
        for filename in filenames:
            if not exclude.search(filename):
                files.append(os.path.relpath(os.path.join(dirpath,filename),module))
    return {module:files}

os.chdir(os.path.split(os.path.abspath(__file__))[0])

setup(name="blogofile_blog",
      description=blogofile_blog.__dist__['pypi_description'],
      version=blogofile_blog.__version__,
      author=blogofile_blog.__dist__["author"],
      url=blogofile_blog.__dist__["url"],
      packages=["blogofile_blog"],
      package_dir = {"blogofile_blog": src_root},
      package_data = find_package_data("blogofile_blog","site_src"),
      include_package_data = True,
      cmdclass = {"sdist":sdist_py2},
      zip_safe=False,
      entry_points = {
        "blogofile.plugins":
            ["blogofile_blog = blogofile_blog"]
        }
      )
