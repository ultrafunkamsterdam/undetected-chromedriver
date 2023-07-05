import time
import logging
logging.basicConfig(level=10)

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait


import undetected_chromedriver as uc


def main(args=None):
    TAKE_IT_EASY = True

    if args:
        TAKE_IT_EASY = (
            args.no_sleeps
        )  # so the demo is 'follow-able' instead of some flashes and boom => done. set it how you like

    if TAKE_IT_EASY:
        sleep = time.sleep
    else:
        sleep = lambda n: print(
            "we could be sleeping %d seconds here, but we don't" % n
        )

    driver = uc.Chrome()
    driver.get("https://www.google.com")

    # accept the terms
    driver.find_elements(By.XPATH, '//*[contains(text(), "Reject all")]')[
        -1
    ].click()  # ;)

    inp_search = driver.find_element(By.XPATH, '//input[@title="Search"]')

    inp_search.send_keys(
        "site:stackoverflow.com undetected chromedriver\n"
    )  # \n as equivalent of ENTER key

    results_container = WebDriverWait(driver, timeout=3).until(
        EC.presence_of_element_located((By.ID, "rso"))
    )

    driver.execute_script(
        """
        let container = document.querySelector('#rso');
        let el = document.createElement('div');
        el.style = 'width:500px;display:block;background:red;color:white;z-index:999;transition:all 2s ease;padding:1em;font-size:1.5em';
        el.textContent = "Excluded from support...!";
        container.insertAdjacentElement('afterBegin', el);
        setTimeout(() => {
            el.textContent = "<<<  OH , CHECK YOUR CONSOLE! >>>"}, 2500)
        
    """
    )

    sleep(2)  # never use this. this is for demonstration purposes only

    for item in results_container.children("a", recursive=True):
        print(item)

    # switching default WebElement for uc.WebElement and do it again
    driver._web_element_cls = uc.UCWebElement

    print("switched to use uc.WebElement. which is more descriptive")
    results_container = driver.find_element(By.ID, "rso")

    # gets only direct children of results_container
    # children is a method unique for undetected chromedriver. it is
    # incompatible when you use regular chromedriver
    for item in results_container.children():
        print(item.tag_name)
        for grandchild in item.children(recursive=True):
            print("\t\t", grandchild.tag_name, "\n\t\t\t", grandchild.text)

    print("lets go to image search")
    inp_search = driver.find_element(By.XPATH, '//input[@name="q"]')
    inp_search.clear()
    inp_search.send_keys("hot girls\n")  # \n as equivalent of ENTER

    body = driver.find_element(By.TAG_NAME, "body")
    body.find_elements(By.XPATH, '//a[contains(text(), "Images")]')[0].click_safe()

    # you can't reuse the body from above, because we are on another page right now
    # so the body above is not attached anymore
    image_search_body = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # gets all images and prints the src
    print("getting image sources data, hold on...")

    for item in image_search_body.children("img", recursive=True):
        print(item.attrs.get("src", item.attrs.get("data-src")), "\n\n")

    USELESS_SITES = [
        "https://www.trumpdonald.org",
        "https://www.isitchristmas.com",
        "https://isnickelbacktheworstbandever.tumblr.com",
        "https://www.isthatcherdeadyet.co.uk",
        "https://whitehouse.gov",
        "https://www.nsa.gov",
        "https://kimjongillookingatthings.tumblr.com",
        "https://instantrimshot.com",
        "https://www.nyan.cat",
        "https://twitter.com",
    ]

    print("opening 9 additinal windows and control them")
    sleep(1)  # never use this. this is for demonstration purposes only
    for _ in range(9):
        driver.window_new()

    print("now we got 10 windows")
    sleep(1)
    print("using the new windows to open 9 other useless sites")
    sleep(1)  # never use this. this is for demonstration purposes only

    for idx in range(1, 10):
        # skip the first handle which is our original window
        print("opening ", USELESS_SITES[idx])
        driver.switch_to.window(driver.window_handles[idx])

        # because of geographical location, (corporate) firewalls and 1001
        # other reasons why a connection could be dropped we will use a try/except clause here.
        try:
            driver.get(USELESS_SITES[idx])
        except WebDriverException as e:
            print(
                (
                    "webdriver exception. this is not an issue in chromedriver, but rather "
                    "an issue specific to your current connection. message:",
                    e.args,
                )
            )
            continue

    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        print("look. %s is working" % driver.current_url)
        sleep(1)  # never use this. it is here only so you can follow along

    print(
        "close windows (including the initial one!), but keep the last new opened window"
    )
    sleep(4)  # never use this. wait until nowsecure passed the bot checks

    for handle in driver.window_handles[:-1]:
        driver.switch_to.window(handle)
        print("look. %s is closing" % driver.current_url)
        sleep(1)
        driver.close()

    # attach to the last open window
    driver.switch_to.window(driver.window_handles[0])
    print("now we only got ", driver.current_url, "left")

    sleep(1)

    driver.get("https://www.nowsecure.nl")

    sleep(5)

    print("lets go to UC project page")
    driver.get("https://www.github.com/ultrafunkamsterdam/undetected-chromedriver")

    
    sleep(2)
    driver.quit()


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--no-sleeps", "-ns", action="store_false")
    a = p.parse_args()
    main(a)
