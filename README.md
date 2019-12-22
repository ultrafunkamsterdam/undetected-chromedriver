# undetected
         888                                                  888         d8b
         888                                                  888         Y8P
         888                                                  888
 .d8888b 88888b.  888d888 .d88b.  88888b.d88b.   .d88b.   .d88888 888d888 888 888  888  .d88b.  888d888
d88P"    888 "88b 888P"  d88""88b 888 "888 "88b d8P  Y8b d88" 888 888P"   888 888  888 d8P  Y8b 888P"
888      888  888 888    888  888 888  888  888 88888888 888  888 888     888 Y88  88P 88888888 888
Y88b.    888  888 888    Y88..88P 888  888  888 Y8b.     Y88b 888 888     888  Y8bd8P  Y8b.     888
 "Y8888P 888  888 888     "Y88P"  888  888  888  "Y8888   "Y88888 888     888   Y88P    "Y8888  888   88888888

BY ULTRAFUNKAMSTERDAM (https://github.com/ultrafunkamsterdam)

Custom Selenium Chromedriver v79 - Passes ALL bot mitigation systems (like distilnetworks.com)



Optimized Selenium Chromedriver patch which does not trigger anti-bot services like Distill Network.
Automatically downloads the driver binary and patches it.
Not tested on Chrome higher than 79!


USAGE
# 1-  by far the easiest
from undetected_chromedriver import Chrome, ChromeOptions
driver = Chrome()
driver.get('https://distilnetworks.com')
# 2- patches current selenium instance (for current session)
import undetected_chromedriver
undetected_chromedriver.install()
from selenium.webdriver import Chrome
driver = Chrome()
driver.get('https://distilnetworks.com')
# 3 - Customized
import undetected_chromedriver
#specify chromedriver version to download and patch
undetected_chromedriver.TARGET_VERSION = 78
# or specify your own chromedriver binary to patch
undetected_chromedriver.install(
    executable_path='c:/users/user1/chromedriver.exe',
    target_version=78
)
from selenium.webdriver import Chrome, ChromeOptions
opts = ChromeOptions()
opts.add_argument(f'--proxy-server=socks5://127.0.0.1:9050')
driver = Chrome(options=opts)
driver.get('https://distilnetworks.com')
a combination of function(s) from this module :)
