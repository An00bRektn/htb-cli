#!/usr/bin/env python3
from setuptools import setup

setup(
    name="htbcli",
    version="0.2",
    description="CLI Wrapper for HTB API",
    author="An00bRektn",
    url="https://github.com/An00bRektn/htb-cli",
    packages=['htbcli', 'htbcli/connectors', 'htbcli/utils'],
    package_data={"htbcli": []},
    entry_points={"console_scripts": ["htbcli=htbcli.__main__:main"]},
    #install_requires=dependencies,
    #dependency_links=dependency_links,
)