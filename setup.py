import os
from setuptools import setup


def readme():
    with open("README.rst") as f:
        return f.read()


with open(os.path.dirname(__file__) + "/VERSION") as f:
    pkgversion = f.read().strip()


setup(
    name = "engcommon",
    version = pkgversion,
    description = "Common Engineering Modules",
    url = "https://github.com/JustAddRobots/engcommon",
    author = "Roderick Constance",
    author_email = "justaddrobots@icloud.com",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    python_requires=">=3",
    packages = [
        "engcommon",
    ],
    install_requires = [
        "numpy",
        "packaging",
    ],
    zip_safe = False,
)
