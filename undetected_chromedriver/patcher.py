#!/usr/bin/env python3
# this module is part of undetected_chromedriver

from distutils.version import LooseVersion
import io
import logging
import os
import random
import re
import secrets
import string
import sys
import time
from urllib.request import urlopen
from urllib.request import urlretrieve
import zipfile


logger = logging.getLogger(__name__)

IS_POSIX = sys.platform.startswith(("darwin", "cygwin", "linux", "linux2"))


class Patcher(object):
    url_repo = "https://chromedriver.storage.googleapis.com"
    zip_name = "chromedriver_%s.zip"
    exe_name = "chromedriver%s"

    platform = sys.platform
    if platform.endswith("win32"):
        zip_name %= "win32"
        exe_name %= ".exe"
    if platform.endswith(("linux", "linux2")):
        zip_name %= "linux64"
        exe_name %= ""
    if platform.endswith("darwin"):
        zip_name %= "mac64"
        exe_name %= ""

    if platform.endswith("win32"):
        d = "~/appdata/roaming/undetected_chromedriver"
    elif "LAMBDA_TASK_ROOT" in os.environ:
        d = "/tmp/undetected_chromedriver"
    elif platform.startswith(("linux","linux2")):
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
        self.executable_path = None
        prefix = secrets.token_hex(8)

        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path, exist_ok=True)

        if not executable_path:
            self.executable_path = os.path.join(
                self.data_path, "_".join([prefix, self.exe_name])
            )

        if not IS_POSIX:
            if executable_path:
                if not executable_path[-4:] == ".exe":
                    executable_path += ".exe"

        self.zip_path = os.path.join(self.data_path, prefix)

        if not executable_path:
            self.executable_path = os.path.abspath(
                os.path.join(".", self.executable_path)
            )

        self._custom_exe_path = False

        if executable_path:
            self._custom_exe_path = True
            self.executable_path = executable_path
        self.version_main = version_main
        self.version_full = None

    def auto(self, executable_path=None, force=False, version_main=None):
        """"""
        if executable_path:
            self.executable_path = executable_path
            self._custom_exe_path = True

        if self._custom_exe_path:
            ispatched = self.is_binary_patched(self.executable_path)
            if not ispatched:
                return self.patch_exe()
            else:
                return

        if version_main:
            self.version_main = version_main
        if force is True:
            self.force = force

        try:
            os.unlink(self.executable_path)
        except PermissionError:
            if self.force:
                self.force_kill_instances(self.executable_path)
                return self.auto(force=not self.force)
            try:
                if self.is_binary_patched():
                    # assumes already running AND patched
                    return True
            except PermissionError:
                pass
            # return False
        except FileNotFoundError:
            pass

        release = self.fetch_release_number()
        self.version_main = release.version[0]
        self.version_full = release
        self.unzip_package(self.fetch_package())
        return self.patch()

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
                match = re.search(rb"platform_handle\x00content\x00([0-9.]*)", line)
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

        os.makedirs(self.zip_path, mode=0o755, exist_ok=True)
        with zipfile.ZipFile(fp, mode="r") as zf:
            zf.extract(self.exe_name, self.zip_path)
        os.rename(os.path.join(self.zip_path, self.exe_name), self.executable_path)
        os.remove(fp)
        os.rmdir(self.zip_path)
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

    def is_binary_patched(self, executable_path=None):
        """simple check if executable is patched.

        :return: False if not patched, else True
        """
        executable_path = executable_path or self.executable_path
        with io.open(executable_path, "rb") as fh:
            if b"window.cdc_adoQpoasnfa76pfcZLmcfl_" in fh.read():
                return False
        return True

    def patch_exe(self):
        """
        Patches the ChromeDriver binary

        :return: True on success
        """
        logger.info("patching driver executable %s" % self.executable_path)
        start = time.time()

        cdc_js_replacements = [  # (old, new, end_empty_filler_byte)
            [b"(function () {window.cdc_adoQpoasnfa76pfcZLmcfl_Array = window.Array;"
             b"window.cdc_adoQpoasnfa76pfcZLmcfl_Promise = window.Promise;"
             b"window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol = window.Symbol;}) ();", b"", b" "],

            [b"window.cdc_adoQpoasnfa76pfcZLmcfl_Array ||", b"", b" "],  # b" " = whitespace = does nothing in .js

            [b"window.cdc_adoQpoasnfa76pfcZLmcfl_Promise ||", b"", b" "],

            [b"window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol ||", b"", b" "]
        ]  # https://github.com/search?q=repo%3Achromium%2Fchromium+%2Fcdc_adoQpoasnfa76pfcZLmcfl_%2F&type=code

        # (old, new+filler_bytes) [Make replacement equal in length by appending 'filler bytes'
        for i in cdc_js_replacements:
            diff = len(i[0]) - len(i[1])
            if diff > 0:
                i[1] = i[1] + (i[2] * diff)
            del i[2]

        with io.open(self.executable_path, "r+b") as fh:
            file_bin = fh.read()
            for r in cdc_js_replacements:
                file_bin = file_bin.replace(r[0], r[1])
            fh.seek(0)
            fh.write(file_bin)

        time_taken_s = time.time() - start
        logger.info(f"finished patching driver executable in {time_taken_s:.3f}s")
        return True

    def __repr__(self):
        return "{0:s}({1:s})".format(
            self.__class__.__name__,
            self.executable_path,
        )

    def __del__(self):

        if self._custom_exe_path:
            # if the driver binary is specified by user
            # we assume it is important enough to not delete it
            return
        else:
            timeout = 3  # stop trying after this many seconds
            t = time.monotonic()
            while True:
                now = time.monotonic()
                if now - t > timeout:
                    # we don't want to wait until the end of time
                    logger.debug(
                        "could not unlink %s in time (%d seconds)"
                        % (self.executable_path, timeout)
                    )
                    break
                try:
                    os.unlink(self.executable_path)
                    logger.debug("successfully unlinked %s" % self.executable_path)
                    break
                except (OSError, RuntimeError, PermissionError):
                    time.sleep(0.1)
                    continue
                except FileNotFoundError:
                    break
