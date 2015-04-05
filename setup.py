from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='monobox-player',
    version=get_version('monobox_player/__init__.py'),
    url='https://github.com/oxullo/monobox-player',
    license='GPL',
    author='OXullo Intersecans',
    author_email='x@brainrapers.org',
    description='Monobox player core',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Pykka >= 1.2',
        'requests >= 2.2',
    ],
    entry_points={
            'console_scripts': [
                    'monobox-player = monobox_player.main:run',
            ],
    },
)
