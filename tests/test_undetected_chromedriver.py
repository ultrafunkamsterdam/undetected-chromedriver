import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time  # noqa


def test_undetected_chromedriver():

    import undetected_chromedriver.v2 as uc
    driver = uc.Chrome()
    
    with driver:
        driver.get("https://coinfaucet.eu")
    time.sleep(4) # sleep only used for timing of screenshot
    driver.save_screenshot("coinfaucet.eu.png")

    with driver:
        driver.get("https://cia.gov")
    time.sleep(4) # sleep only used for timing of screenshot
    driver.save_screenshot("cia.gov.png")

    with driver:
        driver.get("https://lhcdn.botprotect.io")
    time.sleep(4) # sleep only used for timing of screenshot
    driver.save_screenshot("notprotect.io.png")

    with driver:
        driver.get("https://www.datadome.co")
    time.sleep(4) # sleep only used for timing of screenshot
    driver.save_screenshot("datadome.co.png")


test_undetected_chromedriver()

