# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='zfs_admin',
    version=version,
    description='Web Admin for ZFS',
    author='Frappe Technologies',
    author_email='hello@frappe.io',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
