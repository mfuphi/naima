#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst

import glob
import os
import sys

import ah_bootstrap
from setuptools import setup

# A dirty hack to get around some early import/configurations ambiguities
if sys.version_info[0] >= 3:
    import builtins
else:
    import __builtin__ as builtins
builtins._ASTROPY_SETUP_ = True

from astropy_helpers.setup_helpers import (
    register_commands,
    get_debug_option,
    get_package_info,
)
from astropy_helpers.git_helpers import get_git_devstr
from astropy_helpers.version_helpers import generate_version_py

# Get some values from the setup.cfg
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser
conf = ConfigParser()
conf.read(["setup.cfg"])
metadata = dict(conf.items("metadata"))

PACKAGENAME = str(metadata.get("package_name", "packagename"))
DESCRIPTION = metadata.get("description", "Astropy affiliated package")
AUTHOR = metadata.get("author", "")
AUTHOR_EMAIL = metadata.get("author_email", "")
LICENSE = metadata.get("license", "unknown")
URL = metadata.get("url", "http://astropy.org")

# Get the long description from the README.rst file
with open("README.rst", "rt") as f:
    LONG_DESCRIPTION = f.read()

# Store the package name in a built-in variable so it's easy
# to get from other parts of the setup infrastructure
builtins._ASTROPY_PACKAGE_NAME_ = PACKAGENAME

# VERSION should be PEP386 compatible (http://www.python.org/dev/peps/pep-0386)
VERSION = "0.8.4"

# Indicates if this version is a release version
RELEASE = "dev" not in VERSION

if not RELEASE:
    VERSION += get_git_devstr(False)

# Populate the dict of setup command overrides; this should be done before
# invoking any other functionality from distutils since it can potentially
# modify distutils' behavior.
cmdclassd = register_commands(PACKAGENAME, VERSION, RELEASE)

# Freeze build information in version.py
generate_version_py(
    PACKAGENAME, VERSION, RELEASE, get_debug_option(PACKAGENAME)
)

# Treat everything in scripts except README.rst as a script to be installed
scripts = [
    fname
    for fname in glob.glob(os.path.join("scripts", "*"))
    if os.path.basename(fname) != "README.rst"
]

# Get configuration information from all of the various subpackages.
# See the docstring for setup_helpers.update_package_files for more
# details.
package_info = get_package_info()

# Add the project-global data
package_info["package_data"].setdefault(PACKAGENAME, [])
package_info["package_data"][PACKAGENAME].append("data/*")

# Include all .c files, recursively, including those generated by
# Cython, since we can not do this in MANIFEST.in with a "dynamic"
# directory name.
c_files = []
for root, dirs, files in os.walk(PACKAGENAME):
    for filename in files:
        if filename.endswith(".c"):
            c_files.append(
                os.path.join(os.path.relpath(root, PACKAGENAME), filename)
            )
package_info["package_data"][PACKAGENAME].extend(c_files)

install_requires = (
    [
        "astropy>=1.0.2,<4.0",
        "emcee>=2.2.0",
        "corner",
        "matplotlib",
        "scipy",
        "h5py",
        "pyyaml",
    ],
)

setup(
    name=PACKAGENAME,
    version=VERSION,
    description=DESCRIPTION,
    scripts=scripts,
    install_requires=install_requires,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    cmdclass=cmdclassd,
    zip_safe=False,
    use_2to3=False,
    **package_info
)
