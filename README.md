# undetected_chromedriver

BY ULTRAFUNKAMSTERDAM (https://github.com/ultrafunkamsterdam)

Optimized Selenium Chromedriver patch which does not trigger anti-bot services like Distill Network.
Automatically downloads the driver binary and patches it.
Not tested on Chrome higher than 79!
Works only on python 3

## Installation ##
```
pip install  git+https://github.com/ultrafunkamsterdam/undetected-chromedriver.git
```

## Usage ##


#### the easy way (recommended) ####
```python
from undetected_chromedriver import Chrome, ChromeOptions
driver = Chrome()
driver.get('https://distilnetworks.com')
```


#### patches selenium module  ####
Needs to be done before importing from selenium package

```python
import undetected_chromedriver
undetected_chromedriver.install()
from selenium.webdriver import Chrome
driver = Chrome()
driver.get('https://distilnetworks.com')
```` 


#### the customized way ####
```python
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
```



