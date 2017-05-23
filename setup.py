import os
import re

from setuptools import setup
from setuptools import find_packages


here = os.path.abspath(os.path.dirname(__file__))

def get_version(*file_paths):
    """Retrieves the version from catchformats/__init__.py"""
    filename = os.path.join(here, *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("catchformats", "__init__.py")

# Get the long description from the README file
readme = open('README.md').read()

# get the dependencies and installs
with open(os.path.join(here, 'requirements/base.txt')) as f:
    all_reqs = f.read().split('\n')
install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

tests_require = [
    'pytest',
]

setup(
    name='catchformats',
    version=version,
    license="Apache Software License 2.0",
    description='catch input formatters and validators',
    long_description=readme,
    url='https://github.com/nmaekawa/catchformats',
    download_url='https://github.com/nmaekawa/catchformats/tarball/' + version,
    author='nmaekawa',
    author_email='nmaekawa@g.harvard.edu',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['catchpy', 'catch'],
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    dependency_links=dependency_links,
    zip_safe=False,
)
