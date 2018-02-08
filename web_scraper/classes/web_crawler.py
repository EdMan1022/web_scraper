import os
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import sys
from web_scraper.extensions import db
import time
from selenium.webdriver.common.action_chains import ActionChains


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

    audience_reaction_url = "https://www2.mediamonitors.com/v2/app/Reports/AudienceReaction"
    media_selection_id = "txtMediaSelection"

    station_window_id = "ui-id-1"
    station_match_text = "(//*[contains(text(), '{}')] | //*[@value='{}'])"
    station_window_button_class = "ui-dialog-buttonset"

    input_pause_time = .5
    buttonset_text = "OKCancel"
    button_tag = "button"
    ok_text = "OK"
    time_range_id = "ctrlDateRange"

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

    def select_station(self, station_name: str):
        """
        Selects the correct station
        :param station_name:
        :return:
        """
        station_drop_down = self.driver.find_element_by_id(self.media_selection_id)
        station_drop_down.click()
        time.sleep(self.input_pause_time)
        station_window = self.driver.find_element_by_id(self.station_window_id)
        element_list = station_window.find_elements_by_xpath(self.station_match_text.format(station_name,
                                                                                            station_name))
        reduced_element_list = [element for element in element_list if element.text == station_name]
        station_element = reduced_element_list[0]

        station_element.click()

        try:
            buttonset_list = self.driver.find_elements_by_class_name(self.station_window_button_class)
            buttonset = [element for element in buttonset_list if element.text == self.buttonset_text][0]

            buttons = buttonset.find_elements_by_tag_name(self.button_tag)
            ok_button = [element for element in buttons if element.text == self.ok_text][0]

            ok_button.click()
        except IndexError:
            pass

    def button_click(self, button):
        hover = ActionChains(self.driver).move_to_element(button)
        hover.click().perform()

    def select_date(self, date):
        pass


    def select_time_range(self, time_start, time_end):
        time_range_element = self.driver.find_element_by_id(self.time_range_id)
        time_range_buttons = self.driver.find_elements_by_tag_name(self.button_tag)
        start_button = time_range_buttons[0]
        end_button = time_range_buttons[1]
        self.button_click(start_button)
        self.select_date(time_start)

        self.button_click(end_button)
        self.select_date(time_end)









    def update_station_trends(self, station_name: str):

        self.driver.get(self.audience_reaction_url)
        self.select_station(station_name)








