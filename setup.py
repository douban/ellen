from setuptools import setup, find_packages

from ellen import __version__

# http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing
except ImportError:
    pass


with open('README.md') as long_description_file:
    long_description = long_description_file.read()

install_requires = [
    #'pygit2 == 0.20.0',
    'python-magic >= 0.4.3',
    'mime >= 0.0.3',
]

tests_require = [
    'nose',
] + install_requires

dependency_links = [
    # 'git+http://code.dapps.douban.com/pygit2.git@3a8a145f634fb86673fd6df26677622771bcb2d1#egg=pygit2',
    # 'git+https://github.com/douban/pygit2.git@0674872bfe99c9fcf3dfca5a7ac8ecfc2af8bff9#egg=pygit2-douban',
]

setup(
    name='ellen',
    version=__version__,
    description='Ellen is a wrapper of pygit2 and git command.',
    long_description=long_description,
    author='xutao',
    author_email='xutao@douban.com',
    url='https://github.com/douban/ellen',
    license='revised BSD',
    packages=find_packages(exclude=["tests.*", "tests"]),
    keywords=['git', 'pygit2'],
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=install_requires,
    tests_require=tests_require,
    dependency_links=dependency_links,
)
