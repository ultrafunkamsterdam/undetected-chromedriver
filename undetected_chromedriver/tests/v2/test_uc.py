import pytest
from _pytest.fixtures import FixtureRequest
import undetected_chromedriver.v2 as uc

FAILED_SCREENSHOT_NAME = "failed.png"


@pytest.fixture
def head_uc(request: FixtureRequest):
    request.instance.driver = uc.Chrome()

    def teardown():
        request.instance.driver.save_screenshot(FAILED_SCREENSHOT_NAME)
        request.instance.driver.quit()

    request.addfinalizer(teardown)

    return request.instance.driver


@pytest.fixture
def headless_uc(request: FixtureRequest):
    options = uc.ChromeOptions()
    options.headless = True
    request.instance.driver = uc.Chrome(options=options)

    def teardown():
        request.instance.driver.sapipve_screenshot(FAILED_SCREENSHOT_NAME)
        request.instance.driver.quit()

    request.addfinalizer(teardown)

    return request.instance.driver


pytest.main()
