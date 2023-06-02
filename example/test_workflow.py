import time
import logging
import os
logging.basicConfig(level=10)

from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pathlib import Path
import undetected_chromedriver as uc

# due to the randomneess of the chrome install path on the runner when running action, i have to find it manufally
tmp = Path('/tmp')
for item in tmp.glob('chrome*'):
    if item.is_dir():
        path_list = os.environ['PATH'].split(os.pathsep)
        path_list.insert(0, str(item))
        os.environ['PATH'] = os.pathsep.join(path_list)
        
        
        

def main():
    driver = uc.Chrome(headless=True)
    driver.get("https://nowsecure.nl")
    WebDriverWait(driver, 15).until(EC.text_to_be_present_in_element(("css selector", "main h1"), "OH YEAH, you passed!"))
    driver.quit()


if __name__ == "__main__":
    
    main()
    
