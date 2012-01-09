from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='telesur.theme',
      version=version,
      description="Un tema Diazo en Plone 4.1 para el sitio de teleSUR",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='diazo theme plone teleSUR',
      author='',
      author_email='',
      url='https://github.com/desarrollotv/telesur.theme',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['telesur'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.app.theming',
        'collective.nitf',
        'collective.routes',
        'telesur.api',
        ],
      extras_require={
        'test': ['plone.app.testing'],
        },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
