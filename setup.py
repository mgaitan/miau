#!/usr/bin/env python
import os
import setuptools


readme = ''
if os.path.exists('README.md'):
    with open('README.md') as readme_file:
        readme = readme_file.read()

changes = ''
if os.path.exists('CHANGES.md'):
    with open('CHANGES.md') as changes_file:
        changes = changes_file.read()

requirements = []
with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()

test_requirements = []

setuptools.setup(
    name = 'miau',
    version = '0.1.0',
    description = "Remix speeches for fun and profit",
    long_description = '%s\n\n%s' % (readme, changes),
    author = "Martín Gaitán",
    author_email = 'gaitan@gmail.com',
    url = 'https://github.com/mgaitan/miau',
    packages = setuptools.find_packages(),
    package_dir = {'miau': 'miau'},
    include_package_data = True,
    install_requires = requirements,
    entry_points = {
        'console_scripts': [
            'miau = miau:main',
        ]
    },
    license = "BSD",
    keywords = 'miau',
    classifiers = [
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
