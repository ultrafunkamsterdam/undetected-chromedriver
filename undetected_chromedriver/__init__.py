#!/usr/bin/env python3


"""

         888                                                  888         d8b
         888                                                  888         Y8P
         888                                                  888
 .d8888b 88888b.  888d888 .d88b.  88888b.d88b.   .d88b.   .d88888 888d888 888 888  888  .d88b.  888d888
d88P"    888 "88b 888P"  d88""88b 888 "888 "88b d8P  Y8b d88" 888 888P"   888 888  888 d8P  Y8b 888P"
888      888  888 888    888  888 888  888  888 88888888 888  888 888     888 Y88  88P 88888888 888
Y88b.    888  888 888    Y88..88P 888  888  888 Y8b.     Y88b 888 888     888  Y8bd8P  Y8b.     888
 "Y8888P 888  888 888     "Y88P"  888  888  888  "Y8888   "Y88888 888     888   Y88P    "Y8888  888   88888888

BY ULTRAFUNKAMSTERDAM (https://github.com/ultrafunkamsterdam)


##################################################################

Optimized Selenium Chromedriver patch which does not trigger anti-bot services like Distill Network.
Automatically downloads the driver binary and patches it.

Not tested on Chrome higher than 79!

#################################################################


USAGE

# 1-  by far the easiest

from undetected_chromedriver import Chrome, ChromeOptions
driver = Chrome()
driver.get('https://distilnetworks.com')



# 2- patches current selenium instance (for current session)

import undetected_chromedriver
undetected_chromedriver.install()

from selenium.webdriver import Chrome
driver = Chrome()
driver.get('https://distilnetworks.com')


# 3 - Customized

import undetected_chromedriver

#specify chromedriver version to download and patch
undetected_chromedriver.TARGET_VERSION = 78

# or specify your own chromedriver binary to patch
undetected_chromedriver.install(
    executable_path='c:/users/user1/chromedriver.exe',
    target_version=78
)

from selenium.webdriver import Chrome, ChromeOptions
opts = ChromeOptions()
opts.add_argument(f'--proxy-server=socks5://127.0.0.1:9050')
driver = Chrome(options=opts)
driver.get('https://distilnetworks.com')


a combination of function(s) from this module :)

"""

import io
import logging
import os
import sys
import zipfile
from urllib.request import urlopen, urlretrieve

from selenium.webdriver import Chrome as _Chrome
from selenium.webdriver import ChromeOptions as _ChromeOptions


_DL_BASE = "https://chromedriver.storage.googleapis.com/"
TARGET_VERSION = 79
__is_patched__ = 0


class Chrome:
    def __new__(cls, *args, **kwargs):
        if not ChromeDriverManager.installed:
            ChromeDriverManager(*args, **kwargs).install()
        if not ChromeDriverManager.selenium_patched:
            ChromeDriverManager(*args, **kwargs).patch_selenium_webdriver()
        instance = object.__new__(_Chrome)
        instance.__init__(*args, **kwargs)
        instance.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
            },
        )
        original_user_agent_string = instance.execute_script(
            "return navigator.userAgent"
        )
        instance.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": original_user_agent_string.replace("Headless", ""),
                "platform": "Windows",
            },
        )
        print(f"starting webdriver instance Chrome({args}, {kwargs})")
        return instance


class ChromeOptions:
    def __new__(cls, *args, **kwargs):
        if not ChromeDriverManager.installed:
            ChromeDriverManager(*args, **kwargs).install()
        if not ChromeDriverManager.selenium_patched:
            ChromeDriverManager(*args, **kwargs).patch_selenium_webdriver()
        instance = object.__new__(_ChromeOptions)
        instance.__init__()
        instance.add_argument("start-maximized")
        instance.add_experimental_option("excludeSwitches", ["enable-automation"])
        instance.add_experimental_option("useAutomationExtension", False)
        print(f"starting options instance ChromeOptions({args}, {kwargs})")
        return instance

    # return _ChromeOptions()


class ChromeDriverManager(object):
    installed = False
    selenium_patched = False

    def __init__(self, executable_path=None, target_version=None, *args, **kwargs):
        self.executable_path = executable_path or "chromedriver.exe"
        self.platform = sys.platform
        self.target_version = target_version

    def patch_selenium_webdriver(self_):
        """
        Patches existing webdriver path on <executable_path> OR if executable_path is None, will download
        and patch a new webdriver binary for chrome  <version_int> (automatically finds latest release of main version)

        :param str executable_path: OPTIONAL path to existing chromedriver executable to patch
        :param int version_int: OPTIONAL target chrome main version. default 79
        :return:
        """
        import selenium.webdriver.chrome.service
        import selenium.webdriver
        selenium.webdriver.Chrome = Chrome
        selenium.webdriver.ChromeOptions = ChromeOptions
        logging.warning(
            "Now it is safe to import Chrome and ChromeOptions from selenium"
        )
        self_.__class__.selenium_patched = True

    def install(self, patch_selenium=True):
        """
        Initialize the patch

        This will:
         download chromedriver if not present
         patch the downloaded chromedriver
         patch selenium package if <patch_selenium> is True (default)

        :param patch_selenium: patch selenium webdriver classes for Chrome and ChromeDriver (for current python session)
        :return:
        """
        if (
            not self.__class__.installed
            or not __is_patched__
            or not os.path.exists(self.executable_path)
        ):
            self.fetch_chromedriver()
            self.patch_binary()
            self.__class__.installed = True

        if patch_selenium:
            self.patch_selenium_webdriver()

    def get_release_version_number(self):
        """
        Gets the latest major version available, or the latest major version of self.target_version if set explicitly.

        :return: version string
        """
        path = (
            "LATEST_RELEASE"
            if not self.target_version
            else f"LATEST_RELEASE_{self.target_version}"
        )
        return urlopen(_DL_BASE + path).read().decode()

    def fetch_chromedriver(self):
        """
        Downloads ChromeDriver from source and unpacks the executable

        :return: on success, name of the unpacked executable
        """
        base_ = "chromedriver{}"
        exe_name = base_.format(".exe")
        zip_name = base_.format(".zip")
        ver = self.get_release_version_number()
        urlretrieve(
            f"{_DL_BASE}{ver}/{base_.format(f'_{self.platform}')}.zip",
            filename=zip_name,
        )
        with zipfile.ZipFile(zip_name) as zf:
            zf.extract(exe_name)
        os.remove(zip_name)
        return exe_name

    def patch_binary(self):
        """
        Patches the ChromeDriver binary

        :return: False on failure, binary name on success
        """
        if self.__class__.installed:
            return

        with io.open(self.executable_path, "r+b") as binary:
            for line in iter(lambda: binary.readline(), b""):
                if b"cdc_" in line:
                    binary.seek(-len(line), 1)
                    line = b"  var key = '$azc_abcdefghijklmnopQRstuv_';\n"
                    binary.write(line)
                    __is_patched__ = 1
                    break
            else:
                return False
            return True


def install(executable_path=None, target_version=TARGET_VERSION, *args, **kwargs):
    ChromeDriverManager(executable_path, target_version, *args, **kwargs).install()
