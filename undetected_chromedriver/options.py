#!/usr/bin/env python3
# this module is part of undetected_chromedriver


import json
import os
from functools import reduce

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

    def _undot_key(self, key, value):
        """turn a (dotted key, value) into a proper nested dict"""
        if "." in key:
            key, rest = key.split(".", 1)
            value = self._undot_key(rest, value)
        return {key: value}

    def handle_prefs(self, user_data_dir):
        if prefs := self.experimental_options.get("prefs"):

            default_path = os.path.join(user_data_dir, "Default")
            os.makedirs(default_path, exist_ok=False)

            # undot prefs dict keys
            undot_prefs = reduce(
                lambda d1, d2: {**d1, **d2},  # merge dicts
                (self._undot_key(key, value) for key, value in prefs.items()),
            )

            prefs_file = os.path.join(default_path, "Preferences")
            if os.path.exists(prefs_file):
                with open(prefs_file, encoding="latin1", mode="r") as f:
                    undot_prefs.update(json.load(f))

            with open(prefs_file, encoding="latin1", mode="w") as f:
                json.dump(undot_prefs, f)

            # remove the experimental_options to avoid an error
            del self._experimental_options["prefs"]

    @classmethod
    def from_options(cls, options):
        o = cls()
        o.__dict__.update(options.__dict__)
        return o
