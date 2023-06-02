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

driver = uc.Chrome(headless=True)
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



    
# def main():
    
#     # due to the randomneess of the chrome install path on the runner when running action, i have to find it manufally
    
    
#     time.sleep(5)
#     driver = uc.Chrome(headless=True)
#     driver.get("https://nowsecure.nl")
#     WebDriverWait(driver, 15).until(
#         EC.text_to_be_present_in_element(("css selector", "main h1"), "OH YEAH, you passed!"))
#     driver.quit()


# if __name__ == "__main__":
#     main()
