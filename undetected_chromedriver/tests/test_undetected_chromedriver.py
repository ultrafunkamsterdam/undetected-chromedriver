import logging
import os
import sys
import time  # noqa

from ..v2 import *

logging.basicConfig(level=10)

logger = logging.getLogger('TEST')
logger.setLevel(20)


def test_quick():
    import undetected_chromedriver.v2 as uc

    print('uc module: ', uc)
    # options = selenium.webdriver.ChromeOptions()
    options = uc.ChromeOptions()

    options.add_argument('--user-data-dir=c:\\temp')
    options.binary_location = uc.find_chrome_executable()
    driver = uc.Chrome(executable_path='./chromedriver.exe', options=options,
                       service_log_path='c:\\temp\\service.log.txt')
    while True:
        sys.stdin.read()


def test_undetected_chromedriver():
    import undetected_chromedriver.v2 as uc

    driver = uc.Chrome()

    with driver:
        driver.get("https://coinfaucet.eu")
    time.sleep(4)  # sleep only used for timing of screenshot
    driver.save_screenshot("coinfaucet.eu.png")

    with driver:
        driver.get("https://cia.gov")
    time.sleep(4)  # sleep only used for timing of screenshot
    driver.save_screenshot("cia.gov.png")

    with driver:
        driver.get("https://lhcdn.botprotect.io")
    time.sleep(4)  # sleep only used for timing of screenshot
    driver.save_screenshot("notprotect.io.png")

    with driver:
        driver.get("https://www.datadome.co")
    time.sleep(4)  # sleep only used for timing of screenshot
    driver.save_screenshot("datadome.co.png")

# test_quick()
# #test_undetected_chromedriver()
