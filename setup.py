try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

#tests_require = ['pytest', 'Sphinx']

long_description = """
Tangle is a library for building directed data flow graphs.
"""


setup(name="Tangle",
      description="Tangle - Dataflow graph",
      long_description=long_description,
      license="MIT",
      version="0.1",
      author="Gustav Nordman",
      author_email="gustav.nordman@gmail.com",
      maintainer="Gustav Nordman",
      maintainer_email="gustav.nordman@gmail.com",
      url="https://github.com/ltron/tangle",
      packages=['tangle'],
      #tests_require=tests_require,
      #extras_require={
      #    'test': tests_require,
      #},
      classifiers=[
          'Programming Language :: Python :: 3',
])
