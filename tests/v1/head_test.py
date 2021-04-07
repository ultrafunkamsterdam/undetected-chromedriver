import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


TIMEOUT = 10


@pytest.mark.usefixtures("head_uc")
class TestBotCheck:
    def test_bot_protect_io(self):
        driver: WebDriver = self.driver  # type: ignore
        driver.get("https://lhcdn.botprotect.io")
        msg = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_element_located((By.ID, "msg"))
        )
        print(msg.text)
        assert "You are human." in msg.text
