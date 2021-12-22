#!/usr/bin/env python3
# this module is part of undetected_chromedriver


import os
from selenium.webdriver.chromium.options import ChromiumOptions as _ChromiumOptions


class ChromeOptions(_ChromiumOptions):
    _session = None
    _user_data_dir = None

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

    @classmethod
    def from_options(cls, options):
        o = cls()
        o.__dict__.update(options.__dict__)
        return o
