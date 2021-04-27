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
import string
import subprocess
import sys
import tempfile
import time
import zipfile
import shutil
from distutils.version import LooseVersion
from urllib.request import urlopen, urlretrieve

import selenium.webdriver.chrome.service
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.common.service
import selenium.webdriver.remote.webdriver
from selenium.webdriver.chrome.options import Options as _ChromeOptions

__all__ = ("Chrome", "ChromeOptions", "Patcher", "find_chrome_executable")

IS_POSIX = sys.platform.startswith(("darwin", "cygwin", "linux"))

logger = logging.getLogger("uc")
logger.setLevel(logging.getLogger().getEffectiveLevel())


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


class Chrome(object):
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
        keep_alive=True,
        keep_user_data_dir=False,
        log_level=0,
        emulate_touch=False,
    ):

        p = Patcher.auto(executable_path=executable_path)
        # p.auto(False)

        self._patcher = p
        self.port = port
        self.process = None
        self.browser_args = None
        self._rcount = 0
        self._rdiff = 10
        self.keep_user_data_dir = keep_user_data_dir

        debug_port = selenium.webdriver.common.service.utils.free_port()
        debug_host = "127.0.0.1"

        if not options:
            options = selenium.webdriver.chrome.webdriver.Options()

        if not options.debugger_address:
            options.debugger_address = "%s:%d" % (debug_host, debug_port)

        if not options.binary_location:
            options.binary_location = find_chrome_executable()

        if not desired_capabilities:
            desired_capabilities = options.to_capabilities()

        user_data_dir = None

        for arg in options.arguments:
            if "user-data-dir" in arg:
                m = re.search("(?:--)?user-data-dir(?:[ =])?(.*)", arg)
                try:
                    user_data_dir = m[1]
                    logger.debug(
                        "user-data-dir found in user argument %s => %s" % (arg, m[1])
                    )
                    self.keep_user_data_dir = True
                    break
                except IndexError:
                    logger.debug(
                        "no user data dir could be extracted from supplied argument %s "
                        % arg
                    )
        else:
            user_data_dir = os.path.normpath(tempfile.mkdtemp())
            self.keep_user_data_dir = False
            arg = "--user-data-dir=%s" % user_data_dir
            options.add_argument(arg)
            logger.debug(
                "created a temporary folder in which the user-data (profile) will be stored during this\n"
                "session, and added it to chrome startup arguments: %s" % arg
            )
        self.user_data_dir = user_data_dir

        self.options = options

        extra_args = options.arguments

        if options.headless:
            extra_args.append("--headless")
            extra_args.append("--window-size=1920,1080")

        self.browser_args = [
            options.binary_location,
            "--remote-debugging-host=%s" % debug_host,
            "--remote-debugging-port=%s" % debug_port,
            "--log-level=%d" % log_level
            or divmod(logging.getLogger().getEffectiveLevel(), 10)[0],
            *extra_args,
        ]

        self.browser = subprocess.Popen(
            self.browser_args,
            # close_fds="win32" in sys.platform,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.webdriver = selenium.webdriver.chrome.webdriver.WebDriver(
            # executable_path=p.executable_path,
            port=port,
            options=options,
            service_args=service_args,
            desired_capabilities=desired_capabilities,
            service_log_path=service_log_path,
            keep_alive=keep_alive,
        )

        if options.headless:

            orig_get = self.webdriver.get

            logger.info("setting properties for headless")

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

                                Object.defineProperty(Notification, "permission", {
                                    configurable: true,
                                    enumerable: true,
                                        get: () => {
                                            return "unknown"
                                        },       
                                    });
                            """
                        },
                    )

                    logger.info("removing headless from user-agent string")

                    self.execute_cdp_cmd(
                        "Network.setUserAgentOverride",
                        {
                            "userAgent": self.execute_script(
                                "return navigator.userAgent"
                            ).replace("Headless", "")
                        },
                    )
                    logger.info("fixing notifications permission in headless browsers")

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
                return orig_get(*args, **kwargs)

            self.webdriver.get = get_wrapped

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            try:
                return object.__getattribute__(self.webdriver, attr)
            except AttributeError:
                raise

    def __dir__(self):
        return object.__dir__(self) + object.__dir__(self.webdriver)

    def start_session(self, capabilities=None, browser_profile=None):
        if not capabilities:
            capabilities = self.options.to_capabilities()
        self.webdriver.start_session(capabilities, browser_profile)

    # def get_in(self, url: str, delay=2, factor=1):
    #     """
    #     :param url: str
    #     :param delay: int
    #     :param factor: disconnect <factor> seconds after .get()
    #                    too low will disconnect before get() fired.
    #
    #     =================================================
    #
    #     In case you are being detected by some sophisticated
    #     algorithm, and you are the kind that hates losing,
    #     this might be your friend.
    #
    #     this currently works for hCaptcha based systems
    #     (this includes CloudFlare!), and also passes many
    #     custom setups (eg: ticketmaster.com),
    #
    #
    #     Once you are past the first challenge, a cookie is saved
    #     which (in my tests) also worked for other sites, and lasted
    #     my entire session! However, to play safe, i'd recommend to just
    #     call it once for every new site/domain you navigate to.
    #
    #     NOTE:   mileage may vary!
    #             bad behaviour can still be detected, and this program does not
    #             magically "fix" a flagged ip.
    #
    #             please don't spam issues on github! first look if the issue
    #             is not already reported.
    #     """
    #     try:
    #         self.get(url)
    #     finally:
    #         self.service.stop()
    #         # threading.Timer(factor or self.factor, self.close).start()
    #         time.sleep(delay or self.delay)
    #         self.service.start()
    #         self.start_session()
    #
    def quit(self):
        logger.debug("closing webdriver")
        try:
            self.webdriver.quit()
        except Exception:  # noqa
            pass
        try:
            logger.debug("killing browser")
            self.browser.kill()
            self.browser.wait(1)
        except TimeoutError as e:
            logger.debug(e, exc_info=True)
        except Exception:  # noqa
            pass
        if not self.keep_user_data_dir or self.keep_user_data_dir is False:
            for _ in range(3):
                try:
                    logger.debug("removing profile : %s" % self.user_data_dir)
                    shutil.rmtree(self.user_data_dir, ignore_errors=False)
                except FileNotFoundError:
                    pass
                except PermissionError:
                    logger.debug("permission error. files are still in use/locked. retying...")
                else:
                    break
                time.sleep(1)

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
    zip_name = "chromedriver_%s.zip"
    exe_name = "chromedriver%s"

    platform = sys.platform
    if platform.endswith("win32"):
        zip_name %= "win32"
        exe_name %= ".exe"
    if platform.endswith("linux"):
        zip_name %= "linux64"
        exe_name %= ""
    if platform.endswith("darwin"):
        zip_name %= "mac64"
        exe_name %= ""

    if platform.endswith("win32"):
        d = "~/appdata/roaming/undetected_chromedriver"
    elif platform.startswith("linux"):
        d = "~/.local/share/undetected_chromedriver"
    elif platform.endswith("darwin"):
        d = "~/Library/Application Support/undetected_chromedriver"
    else:
        d = "~/.undetected_chromedriver"
    data_path = os.path.abspath(os.path.expanduser(d))

    def __init__(self, executable_path=None, force=False, version_main: int = 0):
        """

        Args:
            executable_path: None = automatic
                             a full file path to the chromedriver executable
            force: False
                    terminate processes which are holding lock
            version_main: 0 = auto
                specify main chrome version (rounded, ex: 82)
        """

        self.force = force

        if not executable_path:
            executable_path = os.path.join(self.data_path, self.exe_name)

        if not IS_POSIX:
            if not executable_path[-4:] == ".exe":
                executable_path += ".exe"

        self.zip_path = os.path.join(self.data_path, self.zip_name)

        self.executable_path = os.path.abspath(os.path.join(".", executable_path))

        self.version_main = version_main
        self.version_full = None

    @classmethod
    def auto(cls, executable_path="./chromedriver", force=False):
        """

        Args:
            force:

        Returns:

        """
        i = cls(executable_path, force=force)
        try:
            os.unlink(i.executable_path)
        except PermissionError:
            if i.force:
                cls.force_kill_instances(i.executable_path)
                return i.auto(force=False)
            try:
                if i.is_binary_patched():
                    # assumes already running AND patched
                    return True
            except PermissionError:
                pass
            # return False
        except FileNotFoundError:
            pass

        release = i.fetch_release_number()
        i.version_main = release.version[0]
        i.version_full = release
        i.unzip_package(i.fetch_package())
        i.patch()
        return i

    def patch(self):
        self.patch_exe()
        return self.is_binary_patched()

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
        with io.open(self.executable_path, "rb") as f:
            for line in iter(lambda: f.readline(), b""):
                match = re.search(br"platform_handle\x00content\x00([0-9.]*)", line)
                if match:
                    return LooseVersion(match[1].decode())

    def fetch_package(self):
        """
        Downloads ChromeDriver from source

        :return: path to downloaded file
        """
        u = "%s/%s/%s" % (self.url_repo, self.version_full.vstring, self.zip_name)
        logger.debug("downloading from %s" % u)
        # return urlretrieve(u, filename=self.data_path)[0]
        return urlretrieve(u)[0]

    def unzip_package(self, fp):
        """
        Does what it says

        :return: path to unpacked executable
        """
        logger.debug("unzipping %s" % fp)
        try:
            os.unlink(self.zip_path)
        except (FileNotFoundError, OSError):
            pass

        os.makedirs(self.data_path, mode=0o755, exist_ok=True)

        with zipfile.ZipFile(fp, mode="r") as zf:
            zf.extract(self.exe_name, os.path.dirname(self.executable_path))
        # os.rename(self.zip_path, self.executable_path)
        os.remove(fp)

        os.chmod(self.executable_path, 0o755)
        return self.executable_path

    @staticmethod
    def force_kill_instances(exe_name):
        """
        kills running instances.
        :param: executable name to kill, may be a path as well

        :return: True on success else False
        """
        exe_name = os.path.basename(exe_name)
        if IS_POSIX:
            r = os.system("kill -f -9 $(pidof %s)" % exe_name)
        else:
            r = os.system("taskkill /f /im %s" % exe_name)
        return not r

    @staticmethod
    def gen_random_cdc():
        cdc = random.choices(string.ascii_lowercase, k=26)
        cdc[-6:-4] = map(str.upper, cdc[-6:-4])
        cdc[2] = cdc[0]
        cdc[3] = "_"
        return "".join(cdc).encode()

    def is_binary_patched(self, executable_path=None):
        """simple check if executable is patched.

        :return: False if not patched, else True
        """
        executable_path = executable_path or self.executable_path
        with io.open(executable_path, "rb") as fh:
            for line in iter(lambda: fh.readline(), b""):
                if b"cdc_" in line:
                    return False
            else:
                return True

    def patch_exe(self):
        """
        Patches the ChromeDriver binary

        :return: False on failure, binary name on success
        """
        logger.info("patching driver executable %s" % self.executable_path)

        linect = 0
        replacement = self.gen_random_cdc()
        with io.open(self.executable_path, "r+b") as fh:
            for line in iter(lambda: fh.readline(), b""):
                if b"cdc_" in line:
                    fh.seek(-len(line), 1)
                    newline = re.sub(b"cdc_.{22}", replacement, line)
                    fh.write(newline)
                    linect += 1
            return linect


# class ChromeOptions(selenium.webdriver.chrome.webdriver.Options):
class ChromeOptions(_ChromeOptions):
    def add_extension_file_crx(self, extension=None):
        if extension:
            extension_to_add = os.path.abspath(os.path.expanduser(extension))
            logger.debug("extension_to_add: %s" % extension_to_add)

        return super().add_extension(r"%s" % extension)
