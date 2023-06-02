import logging
import os
import time
logging.basicConfig(level=10)
logger = logging.getLogger(__name__)

import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pathlib import Path
import undetected_chromedriver as uc


def main():
    
    # due to the randomneess of the chrome install path on the runner when running action, i have to find it manufally
    
    for k,v in os.environ.items():
        logger.info("%s = %s" % (k,v))
    tmp = Path('/tmp').resolve()
    
    for item in tmp.rglob('**'):
        
        print(item)
        
        if item.is_dir():
            if 'chrome-' in item.name:
                path_list = os.environ['PATH'].split(os.pathsep)
                path_list.insert(0, str(item))
                os.environ['PATH'] = os.pathsep.join(path_list)
                break
    time.sleep(5)
    driver = uc.Chrome(headless=True)
    driver.get("https://nowsecure.nl")
    WebDriverWait(driver, 15).until(
        EC.text_to_be_present_in_element(("css selector", "main h1"), "OH YEAH, you passed!"))
    driver.quit()


if __name__ == "__main__":
    main()
