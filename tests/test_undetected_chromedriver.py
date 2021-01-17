import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import undetected_chromedriver.v2 as uc  # noqa
import time  # noqa


def test_undetected_chromedriver():

    # options = uc.ChromeOptions() # todo: get headless mode to work
    # options.headless = True // todo: get headless mode to work

    driver = uc.Chrome()
    try:
        driver.get_in("https://coinfaucet.eu")
    except Exception:
        raise
    driver.save_screenshot("coinfaucet.eu.png")

    # usage variation: context-manager style
    # note: you use normal get() here!
    with driver:
        driver.get("https://coinfaucet.eu")
    time.sleep(3); driver.save_screenshot("coinfaucet.eu.png")

    with driver:
        driver.get("https://cia.gov")
    time.sleep(3); driver.save_screenshot("cia.gov.png")

    with driver:
        driver.get("https://lhcdn.botprotect.io")
    time.sleep(3); driver.save_screenshot("notprotect.io.png")

    with driver:
        driver.get("https://www.datadome.co")
    time.sleep(3); driver.save_screenshot("datadome.co.png")


test_undetected_chromedriver()

