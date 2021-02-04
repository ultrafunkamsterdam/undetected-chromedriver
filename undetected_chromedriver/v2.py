#!/usr/bin/env python3
# this module is part of undetected_chromedriver

"""
V2 beta

whats new: 

    - currently this v2 module will be available as option.
      to use it / test it, you need to alter your imports by appending .v2

    - headless mode not (yet) supported in v2

    example:

    ```python
    import undetected_chromedriver.v2 as uc
    driver = uc.Chrome()
    driver.get('https://somewebsite.xyz')

    # if site is protected by hCaptcha/Cloudflare
    driver.get_in('https://cloudflareprotectedsite.xyz')
    
    # if site is protected by hCaptcha/Cloudflare
    # (different syntax, same function)
    with driver:
        driver.get('https://cloudflareprotectedsite.xyz')
    ```

    tests/example in ../tests/test_undetected_chromedriver.py

"""

from __future__ import annotations

import io
import logging
import os
import random
import re
import shutil
import string
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
import atexit
import contextlib
from distutils.version import LooseVersion
from urllib.request import urlopen, urlretrieve

import selenium.webdriver.chrome.service
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.common.service
import selenium.webdriver.remote.webdriver

__all__ = ("Chrome", "ChromeOptions", "Patcher", "find_chrome_executable")

IS_POSIX = sys.platform.startswith(("darwin", "cygwin", "linux"))

logger = logging.getLogger("uc")


def find_chrome_executable():
    """
    returns the full path to the chrome _browser binary
    may not work if chrome is in a custom folder.

    :return: path to chrome executable
    :rtype: str
    """
    candidates = set()
    if IS_POSIX:
        for item in os.environ.get("PATH").split(os.pathsep):
            for subitem in ("google-chrome", "chromium", "chromium-browser"):
                candidates.add(os.sep.join((item, subitem)))
        if "darwin" in sys.platform:
            candidates.update(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
            )
    else:
        for item in map(
            os.environ.get, ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")
        ):
            for subitem in (
                "Google/Chrome/Application",
                "Google/Chrome Beta/Application",
                "Google/Chrome Canary/Application",
            ):
                candidates.add(os.sep.join((item, subitem, "chrome.exe")))
    for candidate in candidates:
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return os.path.normpath(candidate)


class Chrome(selenium.webdriver.chrome.webdriver.WebDriver):

    __doc__ = (
        """\
    --------------------------------------------------------------------------
    NOTE: 
    Chrome has everything included to work out of the box.
    it does not `need` customizations.
    any customizations MAY lead to trigger bot migitation systems.
    
    --------------------------------------------------------------------------
    """
        + selenium.webdriver.remote.webdriver.WebDriver.__doc__
    )

    _instances = set()

    def __init__(
        self,
        executable_path="./chromedriver",
        port=0,
        options=None,
        service_args=None,
        desired_capabilities=None,
        service_log_path=None,
        chrome_options=None,
        keep_alive=True,
        debug_addr=None,
        user_data_dir=None,
        factor=1,
        delay=2,
        emulate_touch=False,
    ):

        p = Patcher(target_path=executable_path)
        p.auto(False)
        self._patcher = p
        self.factor = factor
        self.delay = delay
        self.port = port
        self.process = None
        self.browser_args = None
        self._rcount = 0
        self._rdiff = 10

        try:
            dbg = debug_addr.split(":")
            debug_host, debug_port = str(dbg[0]), int(dbg[1])
        except AttributeError:
            debug_port = selenium.webdriver.common.service.utils.free_port()
            debug_host = "127.0.0.1"

        if not debug_addr:
            debug_addr = f"{debug_host}:{debug_port}"

        if not user_data_dir:
            user_data_dir = os.path.normpath(tempfile.mkdtemp())

        if not options:
            options = selenium.webdriver.chrome.webdriver.Options()

        if not options.debugger_address:
            options.debugger_address = debug_addr

        if not options.binary_location:
            options.binary_location = find_chrome_executable()

        if not desired_capabilities:
            desired_capabilities = options.to_capabilities()

        self.options = options
        self.user_data_dir = user_data_dir

        extra_args = []
        if options.headless:
            extra_args.append("--headless")
            extra_args.append("--window-size=1920,1080")

        self.browser_args = [
            find_chrome_executable(),
            "--user-data-dir=%s" % user_data_dir,
            "--remote-debugging-host=%s" % debug_host,
            "--remote-debugging-port=%s" % debug_port,
            "--log-level=%d" % divmod(logging.getLogger().getEffectiveLevel(), 10)[0],
            *extra_args,
        ]

        self.browser = subprocess.Popen(
            self.browser_args,
            close_fds="win32" in sys.platform,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        selenium.webdriver.chrome.webdriver.WebDriver.__init__(
            self,
            executable_path=p.target_path,
            port=port,
            options=options,
            service_args=service_args,
            desired_capabilities=desired_capabilities,
            service_log_path=service_log_path,
            chrome_options=chrome_options,
            keep_alive=keep_alive,
        )

        if options.headless:

            orig_get = self.get

            def get_wrapped(*args, **kwargs):
                if self.execute_script("return navigator.webdriver"):
                    self.execute_cdp_cmd(
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
                                });
                            """
                        },
                    )

                    self.execute_cdp_cmd(
                        "Network.setUserAgentOverride",
                        {
                            "userAgent": self.execute_script(
                                "return navigator.userAgent"
                            ).replace("Headless", "")
                        },
                    )
                return orig_get(*args, **kwargs)

            self.get = get_wrapped

        if emulate_touch:
            self.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                           Object.defineProperty(navigator, 'maxTouchPoints', {
                                   get: () => 1
                           })"""
                },
            )

    def start_session(self, capabilities=None, browser_profile=None):
        if not capabilities:
            capabilities = self.options.to_capabilities()
        super().start_session(capabilities, browser_profile)

    def get_in(self, url: str, delay=2, factor=1):
        """
        :param url: str
        :param delay: int
        :param factor: disconnect <factor> seconds after .get()
                       too low will disconnect before get() fired.

        =================================================

        In case you are being detected by some sophisticated
        algorithm, and you are the kind that hates losing,
        this might be your friend.

        this currently works for hCaptcha based systems
        (this includes CloudFlare!), and also passes many
        custom setups (eg: ticketmaster.com),


        Once you are past the first challenge, a cookie is saved
        which (in my tests) also worked for other sites, and lasted
        my entire session! However, to play safe, i'd recommend to just
        call it once for every new site/domain you navigate to.

        NOTE:   mileage may vary!
                bad behaviour can still be detected, and this program does not
                magically "fix" a flagged ip.

                please don't spam issues on github! first look if the issue
                is not already reported.
        """
        try:
            self.get(url)
        finally:
            self.service.stop()
            # threading.Timer(factor or self.factor, self.close).start()
            time.sleep(delay or self.delay)
            self.service.start()
            self.start_session()

    def quit(self):
        try:
            self.browser.kill()
            self.browser.wait(1)
        except TimeoutError as e:
            logger.debug(e, exc_info=True)
        except Exception:  # noqa
            pass
        try:
            super().quit()
        except Exception:  # noqa
            pass
        try:
            shutil.rmtree(self.user_data_dir, ignore_errors=False)
        except PermissionError:
            time.sleep(1)
            self.quit()

    def __del__(self):
        self.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.service.stop()
        # threading.Timer(self.factor, self.service.start).start()
        time.sleep(self.delay)
        self.service.start()
        self.start_session()

    def __hash__(self):
        return hash(self.options.debugger_address)


class Patcher(object):
    url_repo = "https://chromedriver.storage.googleapis.com"

    def __init__(
        self, target_path="./chromedriver", force=False, version_main: int = 0
    ):
        if not IS_POSIX:
            if not target_path[-4:] == ".exe":
                target_path += ".exe"

        self.force = force
        z, e = self.get_package_name()
        if not target_path:
            target_path = e

        self.exename = e
        self.target_path = target_path
        self.zipname = z
        self.version_main = version_main
        self.version_full = None

    def auto(self, force=False):
        try:
            os.unlink(self.target_path)
        except PermissionError:

            if force or self.force:
                self.force_kill_instances()
                return self.auto()

            if self.verify_patch():
                # assumes already running AND patched
                return True
            return False
        except FileNotFoundError:
            pass

        release = self.fetch_release_number()
        self.version_main = release.version[0]
        self.version_full = release
        self.fetch_package()
        self.unzip_package()
        self.patch_exe()
        return self.verify_patch()

    def fetch_release_number(self):
        """
        Gets the latest major version available, or the latest major version of self.target_version if set explicitly.
        :return: version string
        :rtype: LooseVersion
        """
        path = "/latest_release"
        if self.version_main:
            path += f"_{self.version_main}"
        path = path.upper()
        logger.debug("getting release number from %s" % path)
        return LooseVersion(urlopen(self.url_repo + path).read().decode())

    def parse_exe_version(self):
        with io.open(self.target_path, "rb") as f:
            for line in iter(lambda: f.readline(), b""):
                match = re.search(br"platform_handle\x00content\x00([0-9\.]*)", line)
                if match:
                    return LooseVersion(match[1].decode())

    def fetch_package(self):
        """
        Downloads ChromeDriver from source

        :return: path to downloaded file
        """
        u = "%s/%s/%s" % (self.url_repo, self.version_full.vstring, self.zipname)
        logger.debug("downloading from %s" % u)
        zp, *_ = urlretrieve(u, filename=self.zipname)
        return zp

    def unzip_package(self):
        """
        Does what it says

        :return: path to unpacked executable
        """
        logger.debug("unzipping %s" % self.zipname)
        try:
            os.makedirs(os.path.dirname(self.target_path), mode=0o755)
        except OSError:
            pass
        with zipfile.ZipFile(self.zipname, mode="r") as zf:
            zf.extract(self.exename)
        os.rename(self.exename, self.target_path)
        os.remove(self.zipname)
        os.chmod(self.target_path, 0o755)
        return self.target_path

    @staticmethod
    def get_package_name():
        """
        returns a tuple of (zipname, exename) depending on platform.

        :return: (zipname, exename)
        """
        zipname = "chromedriver_%s.zip"
        exe = "chromedriver%s"
        platform = sys.platform
        if platform.endswith("win32"):
            zipname %= "win32"
            exe %= ".exe"
        if platform.endswith("linux"):
            zipname %= "linux64"
            exe %= ""
        if platform.endswith("darwin"):
            zipname %= "mac64"
            exe %= ""
        return zipname, exe

    def force_kill_instances(self):
        """
        kills running instances.

        :param self:
        :return: True on success else False
        """
        if IS_POSIX:
            r = os.system("kill -f -9 $(pidof %s)" % self.exename)
        else:
            r = os.system("taskkill /f /im %s" % self.exename)
        return not r

    @staticmethod
    def gen_random_cdc():
        cdc = random.choices(string.ascii_lowercase, k=26)
        cdc[-6:-4] = map(str.upper, cdc[-6:-4])
        cdc[2] = cdc[0]
        cdc[3] = "_"
        return "".join(cdc).encode()

    def verify_patch(self):
        """simple check if executable is patched.

        :return: False if not patched, else True
        """
        try:
            with io.open(self.target_path, "rb") as fh:
                for line in iter(lambda: fh.readline(), b""):
                    if b"cdc_" in line:
                        return False
            return True
        except FileNotFoundError:
            return False

    def patch_exe(self):
        """
        Patches the ChromeDriver binary

        :return: False on failure, binary name on success
        """

        logger.info("patching driver executable %s" % self.target_path)

        linect = 0
        replacement = self.gen_random_cdc()
        with io.open(self.target_path, "r+b") as fh:
            for line in iter(lambda: fh.readline(), b""):
                if b"cdc_" in line:
                    fh.seek(-len(line), 1)
                    newline = re.sub(b"cdc_.{22}", replacement, line)
                    fh.write(newline)
                    linect += 1
            return linect


class ChromeOptions(selenium.webdriver.chrome.webdriver.Options):
    pass
