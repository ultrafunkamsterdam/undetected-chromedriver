#!/usr/bin/env python3
# this module is part of undetected_chromedriver

from __future__ import annotations

import asyncio
import io
import json
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
    Finds the chrome, chrome beta, chrome canary, chromium executable

    Returns
    -------
    executable_path :  str
        the full file path to found executable

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


class Chrome(selenium.webdriver.Chrome):
    """
    Controls the ChromeDriver and allows you to drive the browser.

    The webdriver file will be downloaded by this module automatically,
    you do not need to specify this. however, you may if you wish.


    Attributes
    ----------


    Methods
    -------

    reconnect()

        this can be useful in case of heavy detection methods
        -stops the chromedriver service which runs in the background
        -starts the chromedriver service which runs in the background
        -recreate session


    start_session(capabilities=None, browser_profile=None)

        differentiates from the regular method in that it does not
        require a capabilities argument. The capabilities are automatically
        recreated from the options at creation time.


    --------------------------------------------------------------------------
        NOTE:
            Chrome has everything included to work out of the box.
            it does not `need` customizations.
            any customizations MAY lead to trigger bot migitation systems.

    --------------------------------------------------------------------------
    """

    _instances = set()

    def __init__(
        self,
        executable_path=None,
        port=0,
        options=None,
        enable_cdp_events=False,
        service_args=None,
        desired_capabilities=None,
        service_log_path=None,
        keep_alive=True,
        log_level=0,
        headless=False,
        emulate_touch=False,
        delay=5,
    ):
        """
        Creates a new instance of the chrome driver.

        Starts the service and then creates new instance of chrome driver.


        Parameters
        ----------
        executable_path: str, optional, default: None - use find_chrome_executable
            Path to the executable. If the default is used it assumes the executable is in the $PATH

        port: int, optional, default: 0
            port you would like the service to run, if left as 0, a free port will be found.

        options: ChromeOptions, optional, default: None - automatic useful defaults
            this takes an instance of ChromeOptions, mainly to customize browser behavior.
            anything other dan the default, for example extensions or startup options
            are not supported in case of failure, and can probably lowers your undetectability.

        enable_cdp_events: bool, default: False
            :: currently for chrome only
            this enables the handling of wire messages
            when enabled, you can subscribe to CDP events by using:

                driver.on_cdp_event("Network.dataReceived", yourcallback)
                # yourcallback is an callable which accepts exactly 1 dict as parameter

        service_args: list of str, optional, default: None
            arguments to pass to the driver service

        desired_capabilities: dict, optional, default: None - auto from config
            Dictionary object with non-browser specific capabilities only, such as "item" or "loggingPref".

        service_log_path: str, optional, default: None
             path to log information from the driver.

        keep_alive: bool, optional, default: True
             Whether to configure ChromeRemoteConnection to use HTTP keep-alive.

        log_level: int, optional, default: adapts to python global log level

        headless: bool, optional, default: False
            can also be specified in the options instance.
            Specify whether you want to use the browser in headless mode.
            warning: this lowers undetectability and not fully supported.

        emulate_touch: bool, optional, default: False
            if set to True, patches window.maxTouchPoints to always return non-zero

        delay: int, optional, default: 5
            delay in seconds to wait before giving back control.
            this is used only when using the context manager
            (`with` statement) to bypass, for example CloudFlare.
            5 seconds is a foolproof value.

        """

        patcher = Patcher(executable_path=executable_path)
        patcher.auto()

        if not options:
            options = ChromeOptions()
        try:
            if options.session and options.session is not None:
                #  prevent reuse of options,
                #  as it just appends arguments, not replace them
                #  you'll get conflicts starting chrome
                raise RuntimeError("you cannot reuse the ChromeOptions object")
        except AttributeError:
            pass

        options.session = self

        debug_port = selenium.webdriver.common.service.utils.free_port()
        debug_host = "127.0.0.1"

        if not options.debugger_address:
            options.debugger_address = "%s:%d" % (debug_host, debug_port)

        if enable_cdp_events:
            options.add_experimental_option("goog:loggingPrefs", {"performance": "ALL"})

        options.add_argument("--remote-debugging-host=%s" % debug_host)
        options.add_argument("--remote-debugging-port=%s" % debug_port)

        user_data_dir, language, keep_user_data_dir = None, None, None
        # see if a custom user profile is specified
        for arg in options.arguments:

            if "lang" in arg:
                m = re.search("(?:--)?lang(?:[ =])?(.*)", arg)
                try:
                    language = m[1]
                except IndexError:
                    logger.debug("will set the language to en-US,en;q=0.9")
                    language = "en-US,en;q=0.9"

            if "user-data-dir" in arg:
                m = re.search("(?:--)?user-data-dir(?:[ =])?(.*)", arg)
                try:
                    user_data_dir = m[1]
                    logger.debug(
                        "user-data-dir found in user argument %s => %s" % (arg, m[1])
                    )
                    keep_user_data_dir = True

                except IndexError:
                    logger.debug(
                        "no user data dir could be extracted from supplied argument %s "
                        % arg
                    )

        if not user_data_dir:
            user_data_dir = os.path.normpath(tempfile.mkdtemp())
            keep_user_data_dir = False
            arg = "--user-data-dir=%s" % user_data_dir
            options.add_argument(arg)
            logger.debug(
                "created a temporary folder in which the user-data (profile) will be stored during this\n"
                "session, and added it to chrome startup arguments: %s" % arg
            )

        if not language:
            language = "en-US"

        options.add_argument("--lang=%s" % language)

        if not options.binary_location:
            options.binary_location = find_chrome_executable()

        self._delay = delay

        self.user_data_dir = user_data_dir
        self.keep_user_data_dir = keep_user_data_dir

        if headless or options.headless:
            options.headless = True
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")

        options.add_argument(
            "--log-level=%d" % log_level
            or divmod(logging.getLogger().getEffectiveLevel(), 10)[0]
        )

        # fix exit_type flag to prevent tab-restore nag
        try:
            with open(
                os.path.join(user_data_dir, "Default/Preferences"),
                encoding="latin1",
                mode="r+",
            ) as fs:
                import json

                config = json.load(fs)
                if config["profile"]["exit_type"] is not None:
                    # fixing the restore-tabs-nag
                    config["profile"]["exit_type"] = None
                fs.seek(0, 0)
                fs.write(json.dumps(config, indent=4))
                logger.debug("fixed exit_type flag")
        except Exception as e:
            logger.debug("did not find a bad exit_type flag ")

        self.options = options

        if not desired_capabilities:
            desired_capabilities = options.to_capabilities()

        self.browser = subprocess.Popen(
            [options.binary_location, *options.arguments],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )

        self.webdriver = selenium.webdriver.chrome.webdriver.WebDriver(
            executable_path=patcher.executable_path,
            port=port,
            options=options,
            service_args=service_args,
            desired_capabilities=desired_capabilities,
            service_log_path=service_log_path,
            keep_alive=keep_alive,
        )

        self.reactor = None

        if enable_cdp_events:
            reactor = Reactor(self)
            reactor.start()
            self.reactor = reactor

        # self.__class__._instances.add((self, options))

        if options.headless:

            orig_get = self.get

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
                            
                             Object.defineProperty(window, 'chrome', {
                                     value: new Proxy(window.chrome, {
                                         has: (target,key) => true,
                                         get: (target,key) => {
                                             return {
                                               usingthebestantibotprotection: true
                                               ,
                                               app: {
                                                 isInstalled: false,
                                               },
                                               webstore: {
                                                 onInstallStageChanged: {},
                                                 onDownloadProgress: {},
                                               },
                                               runtime: {
                                                 PlatformOs: {
                                                   MAC: 'mac',
                                                   WIN: 'win',
                                                   ANDROID: 'android',
                                                   CROS: 'cros',
                                                   LINUX: 'linux',
                                                   OPENBSD: 'openbsd',
                                                 },
                                                 PlatformArch: {
                                                   ARM: 'arm',
                                                   X86_32: 'x86-32',
                                                   X86_64: 'x86-64',
                                                 },
                                                 PlatformNaclArch: {
                                                   ARM: 'arm',
                                                   X86_32: 'x86-32',
                                                   X86_64: 'x86-64',
                                                 },
                                                 RequestUpdateCheckStatus: {
                                                   THROTTLED: 'throttled',
                                                   NO_UPDATE: 'no_update',
                                                   UPDATE_AVAILABLE: 'update_available',
                                                 },
                                                 OnInstalledReason: {
                                                   INSTALL: 'install',
                                                   UPDATE: 'update',
                                                   CHROME_UPDATE: 'chrome_update',
                                                   SHARED_MODULE_UPDATE: 'shared_module_update',
                                                 },
                                                 OnRestartRequiredReason: {
                                                   APP_UPDATE: 'app_update',
                                                   OS_UPDATE: 'os_update',
                                                   PERIODIC: 'periodic',
                                                 },
                                               },
                                             }
                                         }
                                     })
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
                self.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": """
                                // fix Notification permission in headless mode
                                Object.defineProperty(Notification, 'permission', { get: () => "default"});
                        """
                    },
                )

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

            self.get = get_wrapped

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            try:
                return object.__getattribute__(self.webdriver, attr)
            except AttributeError:
                raise

    def __dir__(self):
        return object.__dir__(self) + object.__dir__(self)

    def add_cdp_listener(self, event_name, callback):
        if (
            self.reactor
            and self.reactor is not None
            and isinstance(self.reactor, Reactor)
        ):
            self.reactor.add_event_handler(event_name, callback)
            return self.reactor.handlers
        return False

    def reconnect(self):
        try:
            self.service.stop()
        except Exception as e:
            logger.debug(e)

        try:
            self.service.start()
        except Exception as e:
            logger.debug(e)

        try:
            self.start_session()
        except Exception as e:
            logger.debug(e)

    def start_session(self, capabilities=None, browser_profile=None):
        if not capabilities:
            capabilities = self.options.to_capabilities()
        super().start_session(capabilities, browser_profile)

    def quit(self):
        logger.debug("closing webdriver")
        try:
            if self.reactor and isinstance(self.reactor, Reactor):
                self.reactor.event.set()
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
                    logger.debug(
                        "permission error. files are still in use/locked. retying..."
                    )
                else:
                    break
                time.sleep(1)

    def __del__(self):
        logger.debug("Chrome.__del__")
        self.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.service.stop()
        time.sleep(self._delay)
        self.service.start()
        self.start_session()

    def __hash__(self):
        return hash(self.options.debugger_address)

    def find_elements_by_text(self, text: str, selector=None):
        if not selector:
            selector = "*"
        for elem in self.find_elements_by_css_selector(selector):
            try:
                if text.lower() in elem.text.lower():
                    yield elem
            except Exception as e:
                logger.debug("find_elements_by_text: %s" % e)

    def find_element_by_text(self, text: str, selector=None):
        if not selector:
            selector = "*"
        for elem in self.find_elements_by_css_selector(selector):
            try:
                if text.lower() in elem.text.lower():
                    return elem
            except Exception as e:
                logger.debug("find_elements_by_text: {}".format(e))


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
    def auto(cls, executable_path=None, force=False):
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

    def __repr__(self):
        return "{0:s}({1:s})".format(
            self.__class__.__name__,
            self.executable_path,
        )


class ChromeOptions(_ChromeOptions):
    session = None

    def add_extension_file_crx(self, extension=None):
        if extension:
            extension_to_add = os.path.abspath(os.path.expanduser(extension))
            logger.debug("extension_to_add: %s" % extension_to_add)

        return super().add_extension(r"%s" % extension)

    def add_experimental_option(self, name, value):
        self.set_capability(name, value)


class Reactor(threading.Thread):
    def __init__(self, driver: Chrome):
        super().__init__()

        self.driver = driver
        self.loop = asyncio.new_event_loop()

        self.lock = threading.Lock()
        self.event = threading.Event()
        self.daemon = True
        self.handlers = {}

    def add_event_handler(self, method_name, callback: callable):
        """

        Parameters
        ----------
        event_name: str
            example "Network.responseReceived"

        callback: callable
            callable which accepts 1 parameter: the message object dictionary

        Returns
        -------

        """
        with self.lock:
            self.handlers[method_name.lower()] = callback

    @property
    def running(self):
        return not self.event.is_set()

    def run(self):
        try:
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.listen())
        except Exception as e:
            logger.warning("Reactor.run() => %s", e)

    async def listen(self):

        while self.running:

            await asyncio.sleep(0)

            try:
                with self.lock:
                    log_entries = self.driver.get_log("performance")

                for entry in log_entries:

                    try:

                        obj_serialized: str = entry.get("message")
                        obj = json.loads(obj_serialized)
                        message = obj.get("message")
                        method = message.get("method")

                        if "*" in self.handlers:
                            await self.loop.run_in_executor(
                                None, self.handlers["*"], message
                            )
                        elif method.lower() in self.handlers:
                            await self.loop.run_in_executor(
                                None, self.handlers[method.lower()], message
                            )

                        # print(type(message), message)
                    except Exception as e:
                        raise e from None

            except Exception as e:
                if "invalid session id" in str(e):
                    pass
                else:
                    logging.debug("exception ignored :", e)
