import os
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import sys
from web_scraper.extensions import db


class LoginIDs(object):

    user_name_key = "UserName"
    password_key = "Password"

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password


class WebCrawler(object):
    """
    Wraps a headless firefox browser
    """

    moz_env_key = "MOZ_HEADLESS"
    moz_env_value = "1"
    firefox_bin_path = db.app.config['FIREFOX_BINARY_PATH']

    login_ids = LoginIDs(db.app.config['MEDIA_MONITORS_USERNAME'],
                         db.app.config['MEDIA_MONITORS_PASSWORD'])
    login_button_id = "btnLogin"

    def __init__(self):
        os.environ[self.moz_env_key] = self.moz_env_value
        binary = FirefoxBinary(self.firefox_bin_path, log_file=sys.stdout)
        self.driver = webdriver.Firefox(firefox_binary=binary)

    def send_input_by_id(self, element_id, input_keys):
        """
        Finds an element, clears it, and sends new input as string

        :param element_id: html ID of element
        :param input_keys: string to be input by key strokes
        :return:
        """
        element = self.driver.find_element_by_id(element_id)
        element.clear()
        element.send_keys(input_keys)

    def login(self, url: str):
        """
        Logs the browser into a page at the given url

        :param url: address of login page
        :return:
        """

        self.driver.get(url)
        self.send_input_by_id(self.login_ids.user_name_key, self.login_ids.user_name)
        self.send_input_by_id(self.login_ids.password_key, self.login_ids.password)
        submit = self.driver.find_element_by_id(self.login_button_id)
        submit.click()

