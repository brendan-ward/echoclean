import os
from setuptools import setup

setup(
    name='echoclean',
    version='0.1.0',
    packages=['echoclean'],
    url='https://github.com/brendan-ward/echoclean',
    keywords='sonobat, echolocation monitoring',
    license='MIT',
    author='Brendan C. Ward',
    author_email='bcward@astutespruce.com',
    description='Utility to help apply expert rules to sonobat output',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'click',
      'openpyxl==2.5.14',
      'six'
    ],
    extras_require={
      'test': ['pytest'],
    },
    entry_points={
      'console_scripts': 'echoclean=echoclean.cli:cli'
    }
)
