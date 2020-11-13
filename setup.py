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
    description = "Common Engineering Code",
    url = ("git+ssh://git@engcommon.github.com/"
           "JustAddRobots/engcommon.git@{0}").format(pkgversion),
    author = "Roderick Constance",
    author_email = "justaddrobots@icloud.com",
    license = "Private",
    packages = [
        "engcommon",
    ],
    install_requires = [
        "numpy",
        "packaging",
        "PyMySQL",
    ],
    zip_safe = False,
)
