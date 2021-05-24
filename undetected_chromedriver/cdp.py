#!/usr/bin/env python3
# this module is part of undetected_chromedriver

import json
import logging
from collections import Mapping, Sequence

import requests
import websockets

log = logging.getLogger(__name__)


class CDPObjectBase(dict):
    def __init__(self, *a, **kw):
        super().__init__(**kw)
        for k in self:
            if isinstance(self[k], Mapping):
                self[k] = self.__class__(self[k])  # noqa
            elif isinstance(self[k], Sequence) and not isinstance(
                self[k], (str, bytes)
            ):
                self[k] = self[k].__class__(self.__class__(i) for i in self[k])
            else:
                self[k] = self[k]

    def __repr__(self):
        tpl = f"{self.__class__.__name__}(\n\t{{}}\n\t)"
        return tpl.format("\n  ".join(f"{k} = {v}" for k, v in self.items()))


class PageElement(CDPObjectBase):
    pass


class CDP:
    log = logging.getLogger("CDP")

    endpoints = {
        "json": "/json",
        "protocol": "/json/protocol",
        "list": "/json/list",
        "new": "/json/new?{url}",
        "activate": "/json/activate/{id}",
        "close": "/json/close/{id}",
    }

    def __init__(self, options: "ChromeOptions"):
        self.server_addr = "http://{0}:{1}".format(*options.debugger_address.split(":"))

        self._reqid = 0
        self._session = requests.Session()
        self._last_resp = None
        self._last_json = None

        resp = self.get(self.endpoints["json"])
        self.sessionId = resp[0]["id"]
        self.wsurl = resp[0]["webSocketDebuggerUrl"]

    def tab_activate(self, id):
        return self.post(self.endpoints["activate"].format(id=id))

    def tab_list(self):
        retval = self.post(self.endpoints["list"])
        return [PageElement(o) for o in retval]

    def tab_new(self, url):
        return self.post(self.endpoints["new"].format(url=url))

    def tab_close_last_opened(self):
        sessions = self.tab_list()
        opentabs = [s for s in sessions if s["type"] == "page"]
        return self.post(self.endpoints["close"].format(id=opentabs[-1]["id"]))

    async def send(self, method: str, params: dict):
        self._reqid += 1
        async with websockets.connect(self.wsurl) as ws:
            await ws.send(
                json.dumps({"method": method, "params": params, "id": self._reqid})
            )
            self._last_resp = await ws.recv()
            self._last_json = json.loads(self._last_resp)
            self.log.info(self._last_json)

    def get(self, uri):
        resp = self._session.get(self.server_addr + uri)
        try:
            self._last_resp = resp
            self._last_json = resp.json()
        except Exception:
            return
        else:
            return self._last_json

    def post(self, uri):
        resp = self._session.post(self.server_addr + uri)
        try:
            self._last_resp = resp
            self._last_json = resp.json()
        except Exception:
            return self._last_resp

    @property
    def last_json(self):
        return self._last_json
