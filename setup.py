import os
from setuptools import setup, find_packages


long_description = 'Utility to help apply expert rules to sonobat output'


if os.path.exists('README.md'):
    try:
        # Use pypandoc to convert markdown readme to reStructuredText as required by pypi
        # Requires pandoc to be installed.  See: http://johnmacfarlane.net/pandoc/installing.html
        from pypandoc import convert
        read_md = lambda f: convert(f, 'rst', format='md')
        long_description = read_md('README.md')
    except:
        pass

setup(
    name='echoclean',
    version='0.1.0',
    description=u"Utility to help apply expert rules to sonobat output",
    long_description=long_description,
    classifiers=[],
    keywords='sonobat, echolocation monitoring',
    author=u"Brendan Ward",
    author_email='bcward@consbio.org',
    url='https://github.com/consbio/echoclean',
    license='ISC',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'click',
      'openpyxl'
    ],
    extras_require={
      'test': ['pytest'],
    },
    entry_points={
      'console_scripts': 'echoclean=echoclean.cli:cli'
    }
)
