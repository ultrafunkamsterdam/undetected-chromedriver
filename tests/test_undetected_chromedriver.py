from undetected_chromedriver import Chrome


def test_undetected_features_plugins():
    a = Chrome()
    a.get(r"https://google.com")
    assert a.execute_script("return navigator.webdriver") == None
    assert "Headless" not in a.execute_script("return navigator.userAgent")
    assert a.execute_script("window.document.documentElement.getAttribute('webdriver')") == None
    assert all([not key.startswith("cdc_") for key in a.execute_script("return Object.keys(document)")])
