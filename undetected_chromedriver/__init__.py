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

by UltrafunkAmsterdam (https://github.com/ultrafunkamsterdam)

"""

import io
import logging
import os
import sys
import zipfile
from distutils.version import LooseVersion
from urllib.request import urlopen, urlretrieve

from selenium.webdriver import Chrome as _Chrome
from selenium.webdriver import ChromeOptions as _ChromeOptions

logger = logging.getLogger(__name__)


__IS_PATCHED__ = 0
TARGET_VERSION = 0


class Chrome:
    def __new__(cls, *args, **kwargs):

        if not ChromeDriverManager.installed:
            ChromeDriverManager(*args, **kwargs).install()
        if not ChromeDriverManager.selenium_patched:
            ChromeDriverManager(*args, **kwargs).patch_selenium_webdriver()
        if not kwargs.get("executable_path"):
            kwargs["executable_path"] = "./{}".format(
                ChromeDriverManager(*args, **kwargs).executable_path
            )
        if not kwargs.get("options"):
            kwargs["options"] = ChromeOptions()
        instance = object.__new__(_Chrome)
        instance.__init__(*args, **kwargs)
        instance.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
        Object.defineProperty(window, 'navigator', {
            value: new Proxy(navigator, {
              has: (target, key) => (key === 'webdriver' ? false : key in target),
              get: (target, key) =>
                key === 'webdriver'
                  ? undefined
                  : typeof target[key] === 'function'
                  ? target[key].bind(target)
                  : target[key]
            })
        })
                  """
            },
        )
        original_user_agent_string = instance.execute_script(
            "return navigator.userAgent"
        )
        instance.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {"userAgent": original_user_agent_string.replace("Headless", ""),},
        )
        logger.info(f"starting undetected_chromedriver.Chrome({args}, {kwargs})")
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
        logger.info(f"starting undetected_chromedriver.ChromeOptions({args}, {kwargs})")
        return instance


class ChromeDriverManager(object):

    installed = False
    selenium_patched = False
    target_version = None

    DL_BASE = "https://chromedriver.storage.googleapis.com/"

    def __init__(self, executable_path=None, target_version=None, *args, **kwargs):

        _platform = sys.platform

        if TARGET_VERSION:  # user override using global
            self.target_version = TARGET_VERSION
        if target_version:
            self.target_version = target_version  # user override
        if not self.target_version:
            # if target_version still not set, fetch the current major release version
            self.target_version = self.get_release_version_number().version[
                0
            ]  # only major version int

        self._base = base_ = "chromedriver{}"

        exe_name = self._base
        if _platform in ("win32",):
            exe_name = base_.format(".exe")
        if _platform in ("linux",):
            _platform += "64"
            exe_name = exe_name.format("")
        if _platform in ("darwin",):
            _platform = "mac64"
            exe_name = exe_name.format("")
        self.platform = _platform
        self.executable_path = executable_path or exe_name
        self._exe_name = exe_name

    def patch_selenium_webdriver(self_):
        """
        Patches selenium package Chrome, ChromeOptions classes for current session

        :return:
        """
        import selenium.webdriver.chrome.service
        import selenium.webdriver

        selenium.webdriver.Chrome = Chrome
        selenium.webdriver.ChromeOptions = ChromeOptions
        logger.warning("Selenium patched. Safe to import Chrome / ChromeOptions")
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
        if not os.path.exists(self.executable_path):
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
        return LooseVersion(urlopen(self.__class__.DL_BASE + path).read().decode())

    def fetch_chromedriver(self):
        """
        Downloads ChromeDriver from source and unpacks the executable

        :return: on success, name of the unpacked executable
        """
        base_ = self._base
        zip_name = base_.format(".zip")
        ver = self.get_release_version_number().vstring
        if os.path.exists(self.executable_path):
            return self.executable_path
        urlretrieve(
            f"{self.__class__.DL_BASE}{ver}/{base_.format(f'_{self.platform}')}.zip",
            filename=zip_name,
        )
        with zipfile.ZipFile(zip_name) as zf:
            zf.extract(self._exe_name)
        os.remove(zip_name)
        if sys.platform != "win32":
            os.chmod(self._exe_name, 0o755)
        return self._exe_name

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
                    __IS_PATCHED__ = 1
                    break
            else:
                return False
            return True


def install(executable_path=None, target_version=None, *args, **kwargs):
    ChromeDriverManager(executable_path, target_version, *args, **kwargs).install()
