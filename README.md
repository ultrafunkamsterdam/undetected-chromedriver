# undetected_chromedriver #

https://github.com/ultrafunkamsterdam/undetected-chromedriver

Optimized Selenium Chromedriver patch which does not trigger anti-bot services like Distill Network / Imperva / DataDome / Botprotect.io
Automatically downloads the driver binary and patches it.

* **Tested until current chrome beta versions**
* **Works also on Brave Browser and many other Chromium based browsers**
* **Python 3.6++**

## Installation ##
```
pip install undetected-chromedriver
```

## Usage ##

To prevent unnecessary hair-pulling and issue-raising, please mind the **[important note at the end of this document](#important-note) .**

<br>

#### The Version 2 way ####
Literally, this is all you have to do. Settings are included and your browser executable found automagically.

```python
import undetected_chromedriver.v2 as uc
driver = uc.Chrome()
with driver:
    driver.get('https://coinfaucet.eu')  # known url using cloudflare's "under attack mode"
```




<br>
<br>

#### the easy way (v1 old stuff) ####
```python
import undetected_chromedriver as uc
driver = uc.Chrome()
driver.get('https://distilnetworks.com')
```



#### target specific chrome version  (v1 old stuff) ####
```python
import undetected_chromedriver as uc
uc.TARGET_VERSION = 85
driver = uc.Chrome()
```


#### monkeypatch mode  (v1 old stuff) ####
Needs to be done before importing from selenium package

```python
import undetected_chromedriver as uc
uc.install()

from selenium.webdriver import Chrome
driver = Chrome()
driver.get('https://distilnetworks.com')

```


#### the customized way  (v1 old stuff) ####
```python
import undetected_chromedriver as uc

#specify chromedriver version to download and patch
uc.TARGET_VERSION = 78    

# or specify your own chromedriver binary (why you would need this, i don't know)

uc.install(
    executable_path='c:/users/user1/chromedriver.exe',
)

opts = uc.ChromeOptions()
opts.add_argument(f'--proxy-server=socks5://127.0.0.1:9050')
driver = uc.Chrome(options=opts)
driver.get('https://distilnetworks.com')
```


#### datadome.co example  (v1 old stuff) ####
These guys have actually a powerful product, and a link to this repo, which makes me wanna test their product.
Make sure you use a "clean" ip for this one. 
```python
#
# STANDARD selenium Chromedriver
#
from selenium import webdriver
chrome = webdriver.Chrome()
chrome.get('https://datadome.co/customers-stories/toppreise-ends-web-scraping-and-content-theft-with-datadome/')
chrome.save_screenshot('datadome_regular_webdriver.png')
True   # it caused my ip to be flagged, unfortunately


#
# UNDETECTED chromedriver (headless,even)
#
import undetected_chromedriver as uc
options = uc.ChromeOptions()
options.headless=True
options.add_argument('--headless')
chrome = uc.Chrome(options=options)
chrome.get('https://datadome.co/customers-stories/toppreise-ends-web-scraping-and-content-theft-with-datadome/')
chrome.save_screenshot('datadome_undetected_webddriver.png')

```
**Check both saved screenhots [here](https://imgur.com/a/fEmqadP)**



## important note  (v1 old stuff) ####

Due to the inner workings of the module, it is needed to browse programmatically (ie: using .get(url) ). Never use the gui to navigate. Using your keybord and mouse for navigation causes possible detection! New Tabs: same story. If you really need multi-tabs, then open the tab with the blank page (hint: url is  `data:,`  including comma, and yes, driver accepts it) and do your thing as usual. If you follow these "rules" (actually its default behaviour), then you will have a great time for now. 

TL;DR and for the visual-minded:

```python
In [1]: import undetected_chromedriver as uc
In [2]: driver = uc.Chrome()
In [3]: driver.execute_script('return navigator.webdriver')
Out[3]: True  # Detectable
In [4]: driver.get('https://distilnetworks.com') # starts magic
In [4]: driver.execute_script('return navigator.webdriver')
In [5]: None  # Undetectable!
```
## end important note ##



