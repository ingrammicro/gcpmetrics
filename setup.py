#!/usr/bin/env python

import os
from setuptools import setup
from apbvt import testset  # tests to be included into the package

PACKAGE_NAME = 'gcpmetrics'
PACKAGE_VERSION = '1.0'
DESCRIPTION = 'Google Cloud Platform Metrics'


def __find_package_data(folder):
    add_extensions = ['.schema', '.html', '.js', '.css', '.xml', '.jinja', '.bat',
                      '.json', '.png', '.jpg', '.po', '.txt', 'cert.pem', 'key.pem', '.zip']

    file_masks = []
    for subdir, dirs, files in os.walk(folder):
        for f in files:
            name = os.path.join(subdir, f)
            f = f.lower()
            if f.endswith(tuple(add_extensions)):
                path = name[len(folder) + 1:]
                file_mask = os.path.join(os.path.split(path)[0], '*' + os.path.splitext(path)[1])
                if file_mask not in file_masks:
                    file_masks.append(file_mask)

    return file_masks


def get_packages():
    bvt_dirs = ['gcpmetrics']
    bvt_dirs += __find_test_folders()
    return bvt_dirs


def get_package_data():

    data = {
        # 'gcpmetrics': ['*.txt']
    }
    dirs = __find_test_folders()
    for folder in dirs:
        masks = __find_package_data(folder)
        data[folder] = masks
    return data


def get_install_requires():
    with open('requirements.txt') as f:
        return f.readlines()


def version():
    import odintools

    return odintools.version(PACKAGE_VERSION, os.environ.get('BUILD_NUMBER'))

setup(
    name=PACKAGE_NAME,
    author='Odin - Ingram Micro Company',
    author_email='aps@odin.com',
    version_getter=version,
    description=DESCRIPTION,
    url='https://www.odin.com',
    license='BSD',
    packages=get_packages(),
    package_data=get_package_data(),
    install_requires=get_install_requires(),
    zip_safe=False,
    odintools=True,
    entry_points={
        'console_scripts': ['gcpmetrics = gcpmetrics.gcpmetrics:main']
    }
)
