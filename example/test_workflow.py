# coding: utf-8

import time
import logging
import os
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc 
from pathlib import Path


logging.basicConfig(level=10)
logger = logging.getLogger('test')

def main():
    for k,v in os.environ.items():
        logger.info("%s = %s" % (k,v))
    logger.info('==== END ENV ==== ')
    tmp = Path('/tmp').resolve()
    for item in tmp.rglob('**'):    
        logger.info('found %s ' % item)
        
        if item.is_dir():
            if 'chrome-' in item.name:
                
                logger.info('adding %s to PATH' % str(item))
                logger.info('current PATH: %s' % str(os.environ.get('PATH')))
                path_list = os.environ['PATH'].split(os.pathsep)
                path_list.insert(0, str(item))
                os.environ['PATH'] = os.pathsep.join(path_list)
                logger.info('new PATH %s:' % str(os.environ.get('PATH')))
                browser_executable_path = str(item / 'chrome')
                break

    

    driver = uc.Chrome(headless=True, browser_executable_path=browser_executable_path)
    logging.getLogger().setLevel(20)

    driver.get('https://www.nowsecure.nl')

    print(driver.current_url)

    try:
        WebDriverWait(driver,10).until(EC.visibility_of_element_located(("css selector", "body")))
    except TimeoutException:
        pass
    print(driver.current_url)
    try:
        WebDriverWait(driver,10).until(EC.text_to_be_present_in_element(("css selector", "main h1"), "OH YEAH, you passed!"))
    except TimeoutError:
        logging.getLogger().setLevel(20)
        driver.reconnect()
        print(driver.current_url)
        logger.info('trying to save a screenshot via imgur')
    #    driver.reconnect()    
        driver.save_screenshot('/tmp/screenshot.jpg')
        driver.get('https://imgur.com/upload')
        driver.find_element('css selector', 'input').send_keys('/tmp/screenshot.jpg')

        time.sleep(2)
        logger.info('A SCREENSHOT IS SAVED ON %s' % driver.current_url)
        time.sleep(5)
    driver.quit()





if __name__ == "__main__":
    main()
