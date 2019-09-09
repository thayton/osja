import time
import logging

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Excpected condition class for testing whether element is clickable 
# because is_enabled() returns True even though disabled='disabled'
# and get_attribute('disabled') returns 'true' instead of 'disabled'
class element_is_clickable(object):
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        if (element and 
            element.is_displayed() and 
            element.is_enabled() and  
            element.get_attribute('disabled') is None):
            return element
        else:
            return False

class ElemWrapper(object):
    INTERACTIVE_DELAY = 0.25

    def __init__(self, elem):
        ''' elem - WebDriver or WebElement '''
        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self._elem = elem
        self.timeout = 60

    def __getitem__(self, attr):
        return self._elem.get_attribute(attr)

    # Any attribute we don't recognize gets proxyied 
    # over to the WebDriver
    def __getattr__(self, name):
        if hasattr(self._elem, name):
            time.sleep(ElemWrapper.INTERACTIVE_DELAY) # Small delay between selenium calls
            return getattr(self._elem, name)
        raise AttributeError(name)

    @property
    def driver(self):
        ''' Return WebDriver assocated with this element '''
        if isinstance(self._elem, WebDriver):
            return self._elem
        elif isinstance(self._elem, WebElement):
            return self._elem.parent
    
    def wait_until(self, method, timeout=None):
        if timeout == None:
            timeout = self.timeout

        elem = WebDriverWait(self._elem, timeout).until(method)

        if isinstance(elem, WebElement):
            return ElemWrapper(elem)
        else:
            return elem

    def wait_until_not(self, method, timeout=None):
        if timeout == None:
            timeout = self.timeout

        elem = WebDriverWait(self._elem, timeout).until_not(method)

        if isinstance(elem, WebElement):
            return ElemWrapper(elem)
        else:
            return elem

    def get_by(self, id=None, by=()):
        if id:
            by = (By.ID, id)
        elif len(by) == 0:
            by = ('elem', self)
        else:
            assert len(by) == 2

        # 
        # If self is the root WebDriver, then find_element() looks through the 
        # whole DOM. Otherwise it only searches under the current WebElement, 
        # which means we might not find an ID that otherwise exists. Since IDs 
        # are supposed to be unique in a document, we use an XPATH here for ID 
        # searches that ensures we search the entire DOM.
        #
        if by[0] == By.ID:
            by = (By.XPATH, '//*[@id="%s"]' % by[1])

        return by

    def get_clickable_cond(self, id=None, by=()):
        by = self.get_by(id, by)

        if by[0] == 'elem':
            cond = lambda d: by[1] if all(
                [ 
                    by[1], 
                    by[1].is_displayed(), 
                    by[1].is_enabled(), 
                    by[1].get_attribute('disabled') == None 
                ]
            ) else False
        else:
            cond = element_is_clickable(by)

        return cond

    def get_visible_cond(self, id=None, by=()):
        by = self.get_by(id, by)

        if by[0] == 'elem':
            cond = EC.visibility_of(by[1])
        else:
            cond = EC.visibility_of_element_located(by)

        return cond

    def get_staleness_cond(self, id=None, by=()):
        by = self.get_by(id, by)

        if by[0] == 'elem':
            cond = EC.staleness_of(by[1])
        else:
            cond = EC.staleness_of(self.find_element(by[0], by[1]))

        return cond
        
    def wait_until_stale(self, id=None, by=(), timeout=None):
        cond = self.get_staleness_cond(id, by)
        return self.wait_until(cond, timeout)

    def wait_until_clickable(self, id=None, by=(), timeout=None):
        cond = self.get_clickable_cond(id, by)
        return self.wait_until(cond, timeout)

    def wait_until_not_clickable(self, id=None, by=(), timeout=None):
        cond = self.get_clickable_cond(id, by)
        return self.wait_until_not(cond, timeout)

    def wait_until_visible(self,  id=None, by=(), timeout=None):
        cond = self.get_visible_cond(id, by)
        return self.wait_until(cond, timeout)

    def wait_until_not_visible(self,  id=None, by=(), timeout=None):
        cond = self.get_visible_cond(id, by)
        return self.wait_until_not(cond, timeout)

    def find(self, id=None, by=()):
        by = self.get_by(id, by)
        
        if by[0] == 'elem':
            return by[1]
        else:
            return self.wait_until(lambda d: d.find_element(*by))

    def scroll_into_view(self):
        self.location_once_scrolled_into_view
        #self._elem.parent.execute_script("return arguments[0].scrollIntoView();", self._elem);        

    def click(self):
        if not isinstance(self._elem, WebElement):
            raise AttributeError("'WebDriver' object has no attribute 'click'")

        self.wait_until_clickable()

        try:
            self._elem.click()
        except Exception as e:
#            print 'Click generated exception: ', str(e)
#            self._elem.parent.execute_script("arguments[0].click();", self._elem);
            self.javascript_click()

    def javascript_click(self):
        if not isinstance(self._elem, WebElement):
            raise AttributeError("'WebDriver' object has no attribute 'javascript_click'")

        self._elem.parent.execute_script("arguments[0].click();", self._elem);        

    def get_select_options(self, id):
        select = Select(self.find(id))
        options = [ 
            { 'text': o.text, 'value': o.get_attribute('value') }
            for o in select.options
            if o.get_attribute('value')
        ]

        return options

    def select(self, id, value):
        select_elem = self.find(id)
        select = Select(select_elem)

        if select.first_selected_option.get_attribute('value') != value:
            select.select_by_value(value)
            select_elem.wait_until_stale()

            select = Select(self.find(id))
            self.wait_until(
                lambda d: select.first_selected_option.get_attribute('value') == value
            )

def chrome_driver(chrome_path, chromedriver_path):
        chrome_options = Options()
        #chrome_options.add_argument('headless')
        chrome_options.add_argument('disable-extensions')
        chrome_options.add_argument('window-size=1200x600')
        chrome_options.binary_location = chrome_path

        driver = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=chrome_options)
        return driver

