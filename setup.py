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

from setuptools import setup


setup(
    name="undetected-chromedriver",
    version="1.5.0",
    packages=["undetected_chromedriver"],
    install_requires=["selenium",],
    url="https://github.com/ultrafunkamsterdam/undetected_chromedriver",
    license="GPL-3.0",
    author="UltrafunkAmsterdam",
    author_email="info@blackhat-security.nl",
    description="""
                Optimized Selenium/Chromedriver drop-in replacement for selenium.webdriver which does not trigger anti-bot services like Distil / CloudFlare / Imperva / DataDome / Botprotect.io and such.
                All required anti-detection settings are built-in and ready to use, yet overridable if you\'d really want.
                
                Please note: results may vary, and depend on a lot of factors like settings, network, plugins, modus operandi. 
                No guarantees of any kind are given, yet I can guarantee ongoing and tenacious efforts evading and handling detection algorithms.
                
                For more information check out the README.""",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
