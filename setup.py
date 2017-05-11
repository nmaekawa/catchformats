from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

def get_version(*file_paths):
    """Retrieves the version from annotation/__init__.py"""
    filename = os.path.join(here, *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("catch_formats", "__init__.py")

# Get the long description from the README file
readme = open('README.md').read()

# get the dependencies and installs
with open(path.join(here, 'requirements/base.txt')) as f:
    all_reqs = f.read().split('\n')
install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

with open(path.join(here, 'requirements/test.txt')) as f:
    test_reqs = f.read().split('\n')
tests_require = [x.strip() for x in test_reqs]

setup(
    name='catch_formats',
    version=version,
    license="Apache Software License 2.0",
    description='catch input formatters and validators',
    long_description=readme,
    url='https://github.com/nmaekawa/catch_formats',
    download_url='https://github.com/nmaekawa/catch_formats/tarball/' + __version__,
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
    keywords='catchpy',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    dependency_links=dependency_links,
    zip_safe=False,
)
