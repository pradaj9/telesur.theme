from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='telesur.theme',
      version=version,
      description="Un tema Diazo en Plone 4.1 para el sitio de teleSUR",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone :: 4.1",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python",
        "Topic :: Office/Business :: News/Diary",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='diazo theme plone telesur',
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
        'z3c.jbot',
        'collective.upload',
        ],
      extras_require={
        'test': ['plone.app.testing'],
        },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
