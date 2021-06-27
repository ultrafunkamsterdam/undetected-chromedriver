#!/usr/bin/env python3
# this module is part of undetected_chromedriver

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import selenium.webdriver.chrome.service
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.common.service
import selenium.webdriver.remote.webdriver

from .options import ChromeOptions
from .patcher import IS_POSIX, Patcher
from .reactor import Reactor
from .cdp import CDP

__all__ = ("Chrome", "ChromeOptions", "Patcher", "Reactor", "CDP", "find_chrome_executable")

logger = logging.getLogger("uc")
logger.setLevel(logging.getLogger().getEffectiveLevel())


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
        keep_alive=False,
        log_level=0,
        headless=False,
        delay=5,
        version_main=None,
        patcher_force_close=False,
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

                driver.add_cdp_listener("Network.dataReceived", yourcallback)
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

        version_main: int, optional, default: None (=auto)
            if you, for god knows whatever reason, use 
            an older version of Chrome. You can specify it's full rounded version number
            here. Example: 87 for all versions of 87

        patcher_force_close: bool, optional, default: False
            instructs the patcher to do whatever it can to access the chromedriver binary
            if the file is locked, it will force shutdown all instances.
            setting it is not recommended, unless you know the implications and think
            you might need it.
        """
        patcher = Patcher(executable_path=executable_path, force=patcher_force_close, version_main=version_main)
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
            options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

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

            if options.user_data_dir:
                options.add_argument("--user-data-dir=%s" % options.user_data_dir)
                keep_user_data_dir = True
                logger.debug(
                    "user_data_dir property found in options object: %s" % user_data_dir
                )

            else:
                user_data_dir = os.path.normpath(tempfile.mkdtemp())
                keep_user_data_dir = False
                arg = "--user-data-dir=%s" % user_data_dir
                options.add_argument(arg)
                logger.debug(
                    "created a temporary folder in which the user-data (profile) will be stored during this\n"
                    "session, and added it to chrome startup arguments: %s" % arg
                )

        if not language:
            try:
                import locale

                language = locale.getdefaultlocale()[0].replace("_", "-")
            except Exception:
                pass
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
            options.add_argument("--no-sandbox")
            # fixes "could not connect to chrome" error when running 
            # on linux using privileged user like root (which i don't recommend)
            
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
                config = json.load(fs)
                if config["profile"]["exit_type"] is not None:
                    # fixing the restore-tabs-nag
                    config["profile"]["exit_type"] = None
                fs.seek(0, 0)
                json.dump(config, fs)
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
            close_fds=True,
        )

        super().__init__(
            executable_path=patcher.executable_path,
            port=port,
            options=options,
            service_args=service_args,
            desired_capabilities=desired_capabilities,
            service_log_path=service_log_path,
            keep_alive=keep_alive,
        )
        # intentional
        # self.webdriver = selenium.webdriver.chrome.webdriver.WebDriver(
        #     executable_path=patcher.executable_path,
        #     port=port,
        #     options=options,
        #     service_args=service_args,
        #     desired_capabilities=desired_capabilities,
        #     service_log_path=service_log_path,
        #     keep_alive=keep_alive,
        # )

        self.reactor = None
        if enable_cdp_events:

            if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                logging.getLogger(
                    "selenium.webdriver.remote.remote_connection"
                ).setLevel(20)

            reactor = Reactor(self)
            reactor.start()
            self.reactor = reactor


        if options.headless:
            self._configure_headless()

    def _configure_headless(self):

        orig_get = self.get

        logger.info("setting properties for headless")

        def get_wrapped(*args, **kwargs):

            if self.execute_script("return navigator.webdriver"):
                logger.info("patch navigator.webdriver")
                self.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": """
                        
                            Object.defineProperty(window, 'navigator', {
                                value: new Proxy(navigator, {
                                        has: (target, key) => (key === 'webdriver' ? false : key in target),
                                        get: (target, key) =>
                                                key === 'webdriver' ?
                                                undefined :
                                                typeof target[key] === 'function' ?
                                                target[key].bind(target) :
                                                target[key]
                                        })
                            });
                            
                    """
                    },
                )

                logger.info("patch user-agent string")
                self.execute_cdp_cmd(
                    "Network.setUserAgentOverride",
                    {
                        "userAgent": self.execute_script(
                            "return navigator.userAgent"
                        ).replace("Headless", "")
                    },
                )

            if self.options.mock_permissions:
                logger.info("patch permissions api")

                self.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": """
                                // fix Notification permission in headless mode
                                Object.defineProperty(Notification, 'permission', { get: () => "default"});
                        """
                    },
                )

            if self.options.emulate_touch:
                logger.info("patch emulate touch")

                self.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": """
                            Object.defineProperty(navigator, 'maxTouchPoints', {
                                    get: () => 1
                            })"""
                    },
                )

            if self.options.mock_canvas_fp:
                logger.info("patch HTMLCanvasElement fingerprinting")

                self.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": """
                        (function() {
                            const ORIGINAL_CANVAS = HTMLCanvasElement.prototype[name];
                            Object.defineProperty(HTMLCanvasElement.prototype, name, {
                                    "value": function() {
                                            var shift = {
                                                    'r': Math.floor(Math.random() * 10) - 5,
                                                    'g': Math.floor(Math.random() * 10) - 5,
                                                    'b': Math.floor(Math.random() * 10) - 5,
                                                    'a': Math.floor(Math.random() * 10) - 5
                                            };
                                            var width = this.width,
                                                    height = this.height,
                                                    context = this.getContext("2d");
                                            var imageData = context.getImageData(0, 0, width, height);
                                            for (var i = 0; i < height; i++) {
                                                    for (var j = 0; j < width; j++) {
                                                            var n = ((i * (width * 4)) + (j * 4));
                                                            imageData.data[n + 0] = imageData.data[n + 0] + shift.r;
                                                            imageData.data[n + 1] = imageData.data[n + 1] + shift.g;
                                                            imageData.data[n + 2] = imageData.data[n + 2] + shift.b;
                                                            imageData.data[n + 3] = imageData.data[n + 3] + shift.a;
                                                    }
                                            }
                                            context.putImageData(imageData, 0, 0);
                                            return ORIGINAL_CANVAS.apply(this, arguments);
                                    }
                            });
                        })(this)
                        """
                    },
                )

            if self.options.mock_chrome_global:
                self.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": """
                            
                            Object.defineProperty(window, 'chrome', {
                                value: new Proxy(window.chrome, {
                                        has: (target, key) => true,
                                        get: (target, key) => {
                                                return {
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

            return orig_get(*args, **kwargs)

        self.get = get_wrapped

    def __dir__(self):
        return object.__dir__(self)

    def add_cdp_listener(self, event_name, callback):
        if (
            self.reactor
            and self.reactor is not None
            and isinstance(self.reactor, Reactor)
        ):
            self.reactor.add_event_handler(event_name, callback)
            return self.reactor.handlers
        return False
    
    def clear_cdp_listeners(self):
        if self.reactor and isinstance(self.reactor, Reactor):
            self.reactor.handlers.clear()

    def tab_new(self, url:str):
        """
        this opens a url in a new tab.
        apparently, that passes all tests directly!

        Parameters
        ----------
        url

        Returns
        -------

        """
        if not hasattr(self, 'cdp'):
            from .cdp import CDP
            self.cdp = CDP(self.options)
        self.cdp.tab_new(url)

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
            super().quit()

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

        if hasattr(self, 'keep_user_data_dir') \
            and not self.keep_user_data_dir \
                or self.keep_user_data_dir is False:
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
                except (RuntimeError, OSError) as e:
                    logger.debug(
                        "%s retying..." % e
                    )
                else:
                    break
                time.sleep(.25)

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

    def find_elements_by_text(self, text: str):
        for elem in self.find_elements_by_css_selector("*"):
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
