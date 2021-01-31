#!/usr/bin/env python
import os.path
from setuptools import setup
from collections import OrderedDict
from ajsonrpc import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="ajsonrpc",
    version=__version__,
    url="https://github.com/pavlov99/ajsonrpc",
    project_urls=OrderedDict((
        ("Documentation", "https://ajsonrpc.readthedocs.io"),
        ("Code", "https://github.com/pavlov99/ajsonrpc"),
        ("Issue tracker", "https://github.com/pavlov99/ajsonrpc/issues"),
    )),
    license="MIT",
    author="Kirill Pavlov",
    author_email="k@p99.io",
    packages=["ajsonrpc"],
    entry_points = {
        "console_scripts": [
            "async-json-rpc-server=ajsonrpc.scripts.server:main",
        ],
    },
    include_package_data=True,
    platforms="any",
    python_requires='>=3.5',
    description="Async JSON-RPC 2.0 protocol + server powered by asyncio",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
