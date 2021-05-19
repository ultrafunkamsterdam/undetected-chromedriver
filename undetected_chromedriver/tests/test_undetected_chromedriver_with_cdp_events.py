# coding: utf-8

import logging
import undetected_chromedriver.v2 as uc

logging.basicConfig(level=10)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARN)

driver = uc.Chrome(enable_cdp_events=True)

driver.add_cdp_listener("Network.dataReceived", print)

driver.execute_cdp_cmd("Network.getAllCookies", {})
driver.add_cdp_listener('*', print)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                       "source": """
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
                        """})


driver.get('https://coinfaucet.eu')
driver.reconnect()

with driver:
    driver.get('https://coinfaucet.eu')

import sys
while True:
    sys.stdin.read()

