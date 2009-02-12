from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='TracShell',
      version=version,
      description="A command line shell interface to remote Trac instances.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='trac python utilities',
      author='J Kenneth King',
      author_email='james@agentultra.com',
      url='http://code.google.com/p/tracshell/',
      license='Artistic/GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      data_files=[('/usr/local/bin', ['./bin/tracshell'])],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
