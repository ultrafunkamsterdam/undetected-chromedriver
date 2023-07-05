"""

         888                                                  888         d8b
         888                                                  888         Y8P
         888                                                  888
 .d8888b 88888b.  888d888 .d88b.  88888b.d88b.   .d88b.   .d88888 888d888 888 888  888  .d88b.  888d888
d88P"    888 "88b 888P"  d88""88b 888 "888 "88b d8P  Y8b d88" 888 888P"   888 888  888 d8P  Y8b 888P"
888      888  888 888    888  888 888  888  888 88888888 888  888 888     888 Y88  88P 88888888 888
Y88b.    888  888 888    Y88..88P 888  888  888 Y8b.     Y88b 888 888     888  Y8bd8P  Y8b.     888
 "Y8888P 888  888 888     "Y88P"  888  888  888  "Y8888   "Y88888 888     888   Y88P    "Y8888  888   88888888

BY ULTRAFUNKAMSTERDAM (https://github.com/ultrafunkamsterdam)"""

import codecs
import os
import re

from setuptools import setup


dirname = os.path.abspath(os.path.dirname(__file__))

with codecs.open(
    os.path.join(dirname, "undetected_chromedriver", "__init__.py"),
    mode="r",
    encoding="utf-8",
) as fp:
    try:
        version = re.findall(r"^__version__ = ['\"]([^'\"]*)['\"]", fp.read(), re.M)[0]
    except Exception:
        raise RuntimeError("unable to determine version")

description = (
    "Selenium.webdriver.Chrome replacement with compatiblity for Brave, and other Chromium based browsers.",
    "Not triggered by CloudFlare/Imperva/hCaptcha and such.",
    "NOTE: results may vary due to many factors. No guarantees are given, except for ongoing efforts in understanding detection algorithms.",
)

setup(
    name="undetected-chromedriver",
    version=version,
    packages=["undetected_chromedriver"],
    install_requires=[
        "selenium>=4.9.0",
        "requests",
        "websockets",
    ],
    package_data={"undetected_chromedriver": [os.path.join("example", "example.py")]},
    url="https://github.com/ultrafunkamsterdam/undetected-chromedriver",
    license="GPL-3.0",
    author="UltrafunkAmsterdam",
    author_email="info@blackhat-security.nl",
    description=description,
    long_description=open(os.path.join(dirname, "README.md"), encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
