#!/usr/bin/env python3
# this module is part of undetected_chromedriver

import base64
import os

from selenium.webdriver.chrome.options import Options as _ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class ChromeOptions(_ChromeOptions):
    KEY = "goog:chromeOptions"

    session = None
    emulate_touch = True
    mock_permissions = True
    mock_chrome_global = False
    mock_canvas_fp = True
    _user_data_dir = None

    def __init__(self):
        super().__init__()
        self._arguments = []
        self._binary_location = ""
        self._extension_files = []
        self._extensions = []
        self._experimental_options = {}
        self._debugger_address = None
        self._caps = self.default_capabilities
        self.mobile_options = None
        self.set_capability("pageLoadStrategy", "normal")

    @property
    def user_data_dir(self):
        return self._user_data_dir

    @user_data_dir.setter
    def user_data_dir(self, path: str):
        """
        Sets the browser profile folder to use, or creates a new profile
        at given <path>.

        Parameters
        ----------
        path: str
            the path to a chrome profile folder
            if it does not exist, a new profile will be created at given location
        """
        apath = os.path.abspath(path)
        self._user_data_dir = os.path.normpath(apath)

    @property
    def arguments(self):
        """
        :Returns: A list of arguments needed for the browser
        """
        return self._arguments

    @property
    def binary_location(self) -> str:
        """
        :Returns: The location of the binary, otherwise an empty string
        """
        return self._binary_location

    @binary_location.setter
    def binary_location(self, value: str):
        """
        Allows you to set where the chromium binary lives
        :Args:
         - value: path to the Chromium binary
        """
        self._binary_location = value

    @property
    def debugger_address(self) -> str:
        """
        :Returns: The address of the remote devtools instance
        """
        return self._debugger_address

    @debugger_address.setter
    def debugger_address(self, value: str):
        """
        Allows you to set the address of the remote devtools instance
        that the ChromeDriver instance will try to connect to during an
        active wait.
        :Args:
         - value: address of remote devtools instance if any (hostname[:port])
        """
        self._debugger_address = value

    @property
    def extensions(self):
        """
        :Returns: A list of encoded extensions that will be loaded
        """
        encoded_extensions = []
        for ext in self._extension_files:
            file_ = open(ext, "rb")
            # Should not use base64.encodestring() which inserts newlines every
            # 76 characters (per RFC 1521).  Chromedriver has to remove those
            # unnecessary newlines before decoding, causing performance hit.
            encoded_extensions.append(base64.b64encode(file_.read()).decode("UTF-8"))
            file_.close()
        return encoded_extensions + self._extensions

    def add_extension(self, extension: str):
        """
        Adds the path to the extension to a list that will be used to extract it
        to the ChromeDriver
        :Args:
         - extension: path to the \\*.crx file
        """
        if extension:
            extension_to_add = os.path.abspath(os.path.expanduser(extension))
            if os.path.exists(extension_to_add):
                self._extension_files.append(extension_to_add)
            else:
                raise IOError("Path to the extension doesn't exist")
        else:
            raise ValueError("argument can not be null")

    def add_encoded_extension(self, extension: str):
        """
        Adds Base64 encoded string with extension data to a list that will be used to extract it
        to the ChromeDriver
        :Args:
         - extension: Base64 encoded string with extension data
        """
        if extension:
            self._extensions.append(extension)
        else:
            raise ValueError("argument can not be null")

    @property
    def experimental_options(self) -> dict:
        """
        :Returns: A dictionary of experimental options for chromium
        """
        return self._experimental_options

    def add_experimental_option(self, name: str, value: dict):
        """
        Adds an experimental option which is passed to chromium.
        :Args:
          name: The experimental option name.
          value: The option value.
        """
        self._experimental_options[name] = value

    @property
    def headless(self) -> bool:
        """
        :Returns: True if the headless argument is set, else False
        """
        return "--headless" in self._arguments

    @headless.setter
    def headless(self, value: bool):
        """
        Sets the headless argument
        :Args:
          value: boolean value indicating to set the headless option
        """
        args = {"--headless"}
        if value is True:
            self._arguments.extend(args)
        else:
            self._arguments = list(set(self._arguments) - args)

    @property
    def page_load_strategy(self) -> str:
        return self._caps["pageLoadStrategy"]

    @page_load_strategy.setter
    def page_load_strategy(self, strategy: str):
        if strategy in ["normal", "eager", "none"]:
            self.set_capability("pageLoadStrategy", strategy)
        else:
            raise ValueError(
                "Strategy can only be one of the following: normal, eager, none"
            )

    @property
    def capabilities(self):
        return self._caps

    def set_capability(self, name, value):
        """ Sets a capability """
        self._caps[name] = value

    def to_capabilities(self) -> dict:
        """
        Creates a capabilities with all the options that have been set
        :Returns: A dictionary with everything
        """
        caps = self._caps
        chrome_options = self.experimental_options.copy()
        if self.mobile_options:
            chrome_options.update(self.mobile_options)
        chrome_options["extensions"] = self.extensions
        if self.binary_location:
            chrome_options["binary"] = self.binary_location
        chrome_options["args"] = self._arguments
        if self.debugger_address:
            chrome_options["debuggerAddress"] = self.debugger_address

        caps[self.KEY] = chrome_options

        return caps

    def ignore_local_proxy_environment_variables(self):
        """
        By calling this you will ignore HTTP_PROXY and HTTPS_PROXY from being picked up and used.
        """
        self._ignore_local_proxy = True

    @property
    def default_capabilities(self) -> dict:
        return DesiredCapabilities.CHROME.copy()

    def enable_mobile(
        self,
        android_package: str = None,
        android_activity: str = None,
        device_serial: str = None,
    ):
        """
        Enables mobile browser use for browsers that support it
        :Args:
            android_activity: The name of the android package to start
        """
        if not android_package:
            raise AttributeError("android_package must be passed in")
        self.mobile_options = {"androidPackage": android_package}
        if android_activity:
            self.mobile_options["androidActivity"] = android_activity
        if device_serial:
            self.mobile_options["androidDeviceSerial"] = device_serial

    def add_argument(self, argument):
        """
        Adds an argument to the list
        :Args:
         - Sets the arguments
        """
        if argument:
            self._arguments.append(argument)
        else:
            raise ValueError("argument can not be null")

    @classmethod
    def from_options(cls, options):
        o = cls()
        o.__dict__.update(options.__dict__)
        return o
