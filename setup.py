import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'waitress',
    'simplejson',
    'requests',
    'intermine',
    'cx_oracle',
    'sqlalchemy'
    ]

tests_require = [
    'behave',
    'behaving',
    'pytest',
]

setup(name='SGDBackend',
      version='0.0',
      description='SGDBackend',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Kelley Paskov',
      author_email='kpaskov@stanford.edu',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="sgdbackend",
      extras_require={
        'test': tests_require,
      },
      entry_points="""\
      [paste.app_factory]
      main = sgdbackend:main
      """,
      )
