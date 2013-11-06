from setuptools import setup

from ellen import __version__

setup(name='ellen',
      version=__version__,
      description='Ellen is a wrapper of pygit2 and git command.',
      author='xutao',
      author_email='xutao@douban.com',
      url='http://code.dapps.douban.com/xutao/ellen',
      license='BSD',
      packages=['ellen'],
      keywords=['git', 'pygit2'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],)
