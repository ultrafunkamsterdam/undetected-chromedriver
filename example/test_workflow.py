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

    ####
    # this block is a dirty helper since 
    # in the action runner devices serveral chrome versions exists
    # and i need to ensure it takes the one which is installed 
    # by the task.
    ####
    
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

    ####
    #  test really starts here
    #3##
    
    
    driver = uc.Chrome(headless=True, browser_executable_path=browser_executable_path)
    logging.getLogger().setLevel(10)
    
    driver.get('chrome://version')
    
    driver.save_screenshot('/home/runner/work/_temp/versioninfo.png')
    
    driver.get('chrome://settings/help')
    driver.save_screenshot('/home/runner/work/_temp/helpinfo.png')
    
    driver.get('https://www.google.com')
    driver.save_screenshot('/home/runner/work/_temp/google.com.png')
    
    driver.get('https://bot.incolumitas.com/#botChallenge')
    
    pdfdata = driver.execute_cdp_cmd('Page.printToPDF', {})
    if pdfdata:
        if 'data' in pdfdata:
            data = pdfdata['data']
            import base64
            buffer = base64.b64decode(data)
            with open('/home/runner/work/_temp/report.pdf', 'w+b') as f:
                f.write(buffer)
    
    driver.get('https://www.nowsecure.nl')
    
    logger.info('current url %s' % driver.current_url)
    
    try:
        WebDriverWait(driver,15).until(EC.title_contains('moment'))
    except TimeoutException:
        pass
    
    logger.info('current page source:\n%s' % driver.page_source)
    
    logger.info('current url %s' % driver.current_url)
    
    try:
        WebDriverWait(driver,15).until(EC.title_contains('nowSecure'))
        logger.info('PASSED CLOUDFLARE!')
        
    except TimeoutException:    
        logger.info('timeout')
        print(driver.current_url)
   
    logger.info('current page source:\n%s\n' % driver.page_source)
    
    #logger.info('trying to save a screenshot via imgur')
   
    driver.save_screenshot('/home/runner/work/_temp/nowsecure.png')
    
    #driver.get('https://imgur.com/upload')
    
    #driver.find_element('css selector', 'input').send_keys('/home/runner/work/_temp/nowsecure.png')
    
    #time.sleep(1)
    #logger.info('current url %s' % driver.current_url)
    #time.sleep(1)
    #logger.info(f'A SCREENSHOT IS SAVED ON {driver.current_url}  <<< if this ends onlywith /upload than it failed. after all we are running from a datacenter no human being would ever surf the internet from ')
    #time.sleep(5)
    
    driver.quit()
    







if __name__ == "__main__":
    main()
