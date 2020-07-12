from setuptools import setup, find_packages
# from distutils.core import setup
import os
import re
import sys

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
IS_PY3 = sys.version_info[0] == 3

with open("README.md", "r") as fh:
    long_description = fh.read()


def get_version():
    filename = os.path.join(CUR_DIR, 'yz_utils', '__init__.py')
    with open(filename) as f:
        contents = f.read()
    pattern = r"^__version__ = '(.*?)'$"
    return re.search(pattern, contents, re.MULTILINE).group(1)


# extras_require = {
#     'test': [
#         'pytest>=2.7.1',
#         'flake8>=2.4.0',
#     ],
#     'anyjson': ['anyjson>=0.3.3'],
#     'pendulum': ['pendulum>=2.0.5'],
#     'color': ['colour>=0.0.4'],
#     'ipaddress': ['ipaddr'] if not IS_PY3 else [],
#     'enum': ['enum34'] if sys.version_info < (3, 4) else [],
#     'timezone': ['python-dateutil'],
#     'url': ['furl >= 0.4.1'],
#     'encrypted': ['cryptography>=0.6']
# }

setup(
    name="yz-utils",
    version=get_version(),
    author="CML",
    author_email="caimengli0660@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ml444/yz-utils",
    packages=find_packages('.', exclude=['tests', 'tests.*']),
    # package_dir={'': 'yz_utils'},
    # zip_safe=False,
    # include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # license='MIT',
    # platforms='any',
    install_requires=[
        "pydantic==1.5.1",
        # "redis==3.5.0",
        # "oss2==2.3.1",
        # "aliyun-python-sdk-core-v3==2.13.10",
        # "sqlalchemy-utils>=0.32.21",
        # "pandas==1.0.3",
        # "geetest==3.2.1",
        # "requests==2.18.4",
        # "flask-mail==0.9.1",
    ],
    # extras_require=extras_require,
    python_requires=">=3.6.8"
)

