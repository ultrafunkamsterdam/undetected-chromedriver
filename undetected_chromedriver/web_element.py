import selenium.webdriver.remote.webelement


class WebElement(selenium.webdriver.remote.webelement.WebElement):

    @property
    def attrs(self):
        if not hasattr(self, '_attrs'):
            self._attrs = self._parent.execute_script(
                """
                var items = {}; 
                for (index = 0; index < arguments[0].attributes.length; ++index) 
                {
                 items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value 
                }; 
                return items;
                """, self
            )
        return self._attrs
