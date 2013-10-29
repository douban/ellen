from setuptools import setup

setup(name='ellen',
      version='0.0.1',
      description='Ellen is a wrapper of pygit2 and git command.',
      author='xutao',
      author_email='xutao@douban.com',
      license='BSD',
      packages=['ellen'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],)
