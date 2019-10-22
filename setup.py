# -*- coding: utf-8 -*-
import setuptools
import repl_uploader

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setuptools.setup(
    name="repl_uploader",
    version=repl_uploader.VERSION,
    author="Thiago Weidman",
    author_email="tw@weidman.com.br",
    description="Collection of scripts to upload Replicon expenses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thig0w/replicon",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 4 - Beta ",
    ],
)
