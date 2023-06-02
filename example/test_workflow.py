import time
import logging
logging.basicConfig(level=10)

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import undetected_chromedriver as uc

def main()
    driver = uc.Chrome(browser_executable_path="/opt/hostedtoolcache/chromium/latest/x64/chrome", headless=True)
    driver.get("https://nowsecure.nl")
    WebDriverWait(driver, 15).until(EC.text_to_be_present_in_element(("css selector", "main h1"), "OH YEAH, you passed!"))
    driver.quit()


if __name__ == "__main__":
    
    main(a)
    
