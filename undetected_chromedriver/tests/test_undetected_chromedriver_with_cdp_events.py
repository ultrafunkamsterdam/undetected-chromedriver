# coding: utf-8
import logging
import os
import sys

import undetected_chromedriver.v2 as uc

# it's not required to enable logging for cdp events to work
# but as this is a test, it's good too it all
logging.basicConfig(level=10)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARN)

driver = uc.Chrome(enable_cdp_events=True)

# set the callback to Network.dataReceived to print (yeah not much original)
driver.add_cdp_listener("Network.dataReceived", print)

# example of executing regular cdp commands
driver.execute_cdp_cmd("Network.getAllCookies", {})

# okay another one
driver.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {"source": """  alert('another new document')"""},
)

# set the callback for ALL events (this may slow down execution)
# driver.add_cdp_listener('*', print)


with driver:
    driver.get("https://nowsecure.nl")
driver.save_screenshot("nowsecure.nl.headfull.png")
try:
    os.system("nowsecure.nl.headfull.png")
except:
    pass

driver.quit()

opts = uc.ChromeOptions()
opts.headless = True
driver = uc.Chrome(enable_cdp_events=True, options=opts)

# okay another one
driver.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {"source": """  alert('another new document')"""},
)

driver.add_cdp_listener("*", print)

with driver:
    driver.get("https://nowsecure.nl")
    driver.save_screenshot("nowsecure.nl.headfull.png")
try:
    os.system("nowsecure.nl.headfull.png")
except:
    pass

while True:
    sys.stdin.read()
