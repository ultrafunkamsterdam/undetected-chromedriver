import logging
import sys
import time  # noqa

logging.basicConfig(level=10)

logger = logging.getLogger("TEST")
logger.setLevel(20)

JS_SERIALIZE_FUNCTION = """
decycle=function(n,e){"use strict";var t=new WeakMap;return function n(o,r){var c,i;return void 0!==e&&(o=e(o)),"object"!=typeof o||null===o||o instanceof Boolean||o instanceof Date||o instanceof Number||o instanceof RegExp||o instanceof String?o:void 0!==(c=t.get(o))?{$ref:c}:(t.set(o,r),Array.isArray(o)?(i=[],o.forEach(function(e,t){i[t]=n(e,r+"["+t+"]")})):(i={},Object.keys(o).forEach(function(e){i[e]=n(o[e],r+"["+JSON.stringify(e)+"]")})),i)}(n,"$")};
function replacer(t){try{if(Array.prototype.splice.call(t).length<100){let e={};for(let r in t)e[r]=t[r];return e}}catch(t){}}
return decycle(window)
"""


def test_quick():
    import undetected_chromedriver.v2 as uc

    print("uc module: ", uc)
    # options = selenium.webdriver.ChromeOptions()
    options = uc.ChromeOptions()

    options.add_argument("--user-data-dir=c:\\temp")
    options.binary_location = uc.find_chrome_executable()
    driver = uc.Chrome(
        executable_path="./chromedriver.exe",
        options=options,
        service_log_path="c:\\temp\\service.log.txt",
    )
    while True:
        sys.stdin.read()


def test_undetected_chromedriver():
    import undetected_chromedriver.v2 as uc

    driver = uc.Chrome()

    with driver:

        driver.get("https://nowsecure.nl")
    time.sleep(4)  # sleep only used for timing of screenshot
    driver.save_screenshot("nowsecure.nl.png")

    with driver:
        driver.get("https://cia.gov")
    time.sleep(4)  # sleep only used for timing of screenshot
    driver.save_screenshot("cia.gov.png")

    with driver:
        driver.get("https://lhcdn.botprotect.io")
    time.sleep(4)  # sleep only used for timing of screenshot
    driver.save_screenshot("notprotect.io.png")

    with driver:
        driver.get("https://www.datadome.co")
    time.sleep(4)  # sleep only used for timing of screenshot
    driver.save_screenshot("datadome.co.png")


# test_quick()
# #test_undetected_chromedriver()
