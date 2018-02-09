import os
from selenium import webdriver
from selenium.common import exceptions as sel_exc
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


class DayPart(object):

    def __init__(self, start_time, end_time, days):
        self.start_time = start_time
        self.end_time = end_time
        self.days = days

    def time_range(self):
        return "{} - {}".format(self.start_time, self.end_time)

    def day_text(self):
        if self.days:
            return "All days"


class WebCrawler(object):
    """
    Wraps a headless firefox browser
    """

    station_averages = {}

    moz_env_key = "MOZ_HEADLESS"
    moz_env_value = "1"
    firefox_bin_path = db.app.config['FIREFOX_BINARY_PATH']

    login_ids = LoginIDs(db.app.config['MEDIA_MONITORS_USERNAME'],
                         db.app.config['MEDIA_MONITORS_PASSWORD'])
    login_url = "https://www2.mediamonitors.com/v2/app/Account/LogOn"
    login_button_id = "btnLogin"

    audience_reaction_url = "https://www2.mediamonitors.com/v2/app/Reports/AudienceReaction"
    media_selection_id = "txtMediaSelection"

    station_window_id = "ui-id-1"
    station_match_text = "(//*[contains(text(), '{}')] | //*[@value='{}'])"
    station_window_button_class = "ui-dialog-buttonset"

    input_pause_time = 1.
    wait_time = 3.
    long_wait_time = 6.

    buttonset_text = "OKCancel"
    button_tag = "button"
    ok_text = "OK"
    time_range_id = "ctrlDateRange"

    date_picker_id = "ui-datepicker-div"
    date_picker_ui = None
    datepicker_year_class = "ui-datepicker-year"
    datepicker_month_class = "ui-datepicker-month"
    datepicker_calendar_class = "ui-datepicker-calendar"
    go_button_id = "btnGo"
    average_class_name = "average-panel"
    average_check_class = "checkable show-average-button"
    average_overlay_name = "highcharts-mm-average-overlay"
    tspan_name = "tspan"
    average_text_match = " Average"
    report_sidebar = "report-sidebar"
    daypart_id = "ui-id-3"
    row_tag = 'tr'
    column_tag = 'td'
    score_chart_id = "pnlChart"
    n_screenshot = 0
    loading_message_box_class = "loading-mask-control with-message loading"

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

    def login(self):
        """
        Logs the browser into a page at the given url

        :param url: address of login page
        :return:
        """

        self.driver.get(self.login_url)
        self.send_input_by_id(self.login_ids.user_name_key, self.login_ids.user_name)
        self.send_input_by_id(self.login_ids.password_key, self.login_ids.password)
        submit = self.driver.find_element_by_id(self.login_button_id)
        submit.click()

    def click_select_ok(self):
        try:
            self.screenshot()
            buttonset_list = self.driver.find_elements_by_class_name(self.station_window_button_class)
            buttonset = [element for element in buttonset_list if element.text == self.buttonset_text][0]

            buttons = buttonset.find_elements_by_tag_name(self.button_tag)
            ok_button = [element for element in buttons if element.text == self.ok_text][0]

            ok_button.click()
            self.screenshot()
        except IndexError:
            pass

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
        station_search_element = station_window.find_element_by_class_name('keyword-search-input')
        station_search_element.send_keys(station_name)

        station_window = self.driver.find_element_by_id(self.station_window_id)
        time.sleep(3.)
        element_list = station_window.find_elements_by_xpath(self.station_match_text.format(station_name,
                                                                                            station_name))
        reduced_element_list = [element for element in element_list if element.text == station_name]
        station_element = reduced_element_list[0]
        print(station_element.text)
        station_element.click()
        self.pause()
        self.screenshot()
        self.click_select_ok()
        return False

    def select_time_range(self, time_start, time_end):
        time_range_element = self.driver.find_element_by_id(self.time_range_id)
        time_range_buttons = time_range_element.find_elements_by_tag_name(self.button_tag)
        start_button = time_range_buttons[0]
        end_button = time_range_buttons[1]
        self.button_click(start_button)
        self.select_date(time_start)

        self.button_click(end_button)
        self.select_date(time_end)
        return False

    def select_day_part(self, day_part: DayPart):
        sidebar = self.driver.find_element_by_id(self.report_sidebar)
        daypart_filter = sidebar.find_elements_by_class_name('report-filter-item')[-2]
        daypart_button = daypart_filter.find_elements_by_tag_name(self.button_tag)[0]

        self.button_click(daypart_button)
        self.pause()

        daypart_ui = self.driver.find_element_by_id(self.daypart_id)
        daypart_rows = daypart_ui.find_elements_by_tag_name(self.row_tag)

        for row in daypart_rows:
            columns = row.find_elements_by_tag_name(self.column_tag)

            if len(columns) > 1:
                if columns[1].text == day_part.time_range():
                    if columns[2].text == day_part.day_text():
                        break

        row.click()
        self.click_select_ok()
        return False

    def score_chart_wait(self, station_name):
        wait = True
        while wait:
            self.screenshot('wait')
            print('Waiting')
            time.sleep(self.wait_time)

            try:
                self.driver.find_element_by_class_name(self.loading_message_box_class)
            except sel_exc.NoSuchElementException:
                try:
                    self.screenshot("No message box class")
                    element = self.driver.find_element_by_class_name(self.average_class_name)
                    print(element.text)
                    self.screenshot("Found average check")
                    time.sleep(self.wait_time)
                    self.show_average()
                    self.record_average(station_name)
                    wait = False
                except sel_exc.NoSuchElementException:
                    pass

    def button_click(self, button):
        hover = ActionChains(self.driver).move_to_element(button)
        hover.click().perform()

    def select_date(self, date):

        self.date_picker_ui = self.driver.find_element_by_id(self.date_picker_id)

        self.select_year(date.year)
        self.select_month(date.month)
        self.select_day(date.day)

    @staticmethod
    def select_find(element, option):
        options = element.find_elements_by_tag_name('option')
        select_option = [option_element for option_element in options if option_element.text == option][0]
        select_option.click()

    def select_year(self, year):
        year_select = self.date_picker_ui.find_element_by_class_name(self.datepicker_year_class)
        self.select_find(year_select, str(year))

    def select_month(self, month):
        month_select = self.date_picker_ui.find_element_by_class_name(self.datepicker_month_class)
        options = month_select.find_elements_by_tag_name('option')
        select_option = [
            option_element for option_element in options if option_element.get_property('value') == str(month-1)][0]
        select_option.click()

    def select_day(self, day):
        datepicker_calendar = self.date_picker_ui.find_element_by_class_name(self.datepicker_calendar_class)
        date_links = datepicker_calendar.find_elements_by_tag_name('a')
        date_link = [this_date for this_date in date_links if this_date.text == str(day)][0]
        date_link.click()

    def show_average(self):

        try:
            average_overlay = self.driver.find_element_by_class_name(self.average_overlay_name)
        except sel_exc.NoSuchElementException:
            average_check = self.driver.find_elements_by_class_name(self.average_class_name)[0]
            average_check.click()

    def record_average(self, station_name):
        self.pause()
        average_overlay = self.driver.find_element_by_class_name(self.average_overlay_name)
        average_texts = average_overlay.find_elements_by_tag_name(self.tspan_name)

        average_text_element = [avg_text for avg_text in average_texts if self.average_text_match in avg_text.text][0]
        average_text = average_text_element.text
        average_score = average_text.replace(self.average_text_match, '')
        self.station_averages[station_name] = average_score

    def pause(self):
        time.sleep(self.input_pause_time)

    def screenshot(self, title=None):

        self.n_screenshot += 1
        if title is None:
            title = self.n_screenshot
        else:
            title = "{}_{}".format(title, self.n_screenshot)

        self.driver.get_screenshot_as_file("png_log/test_{}.png".format(title))

    def update_station_trends(self, station_name: str, time_start, time_end,
                              day_part: DayPart):
        self.driver.get(self.audience_reaction_url)

        station_bool = True
        print('station_start')
        while station_bool:
            try:
                station_bool = self.select_station(station_name)
            except sel_exc.NoSuchElementException:
                print('no_element_station')
                pass
            except sel_exc.ElementNotInteractableException:
                print('not_interactable_station')
                pass
            except IndexError:
                print('index_error_station')
                pass

        print('time_start')
        time_range_bool = True
        while time_range_bool:
            try:
                time_range_bool = self.select_time_range(time_start, time_end)
            except sel_exc.NoSuchElementException:
                print('no_element_time')
                pass
            except sel_exc.ElementNotInteractableException:
                print('not_interactable_time')
                pass
        self.select_time_range(time_start, time_end)

        print('day_start')
        day_part_bool = True
        while day_part_bool:
            try:
                day_part_bool = self.select_day_part(day_part)
            except sel_exc.NoSuchElementException:
                print('no_element_day')
                pass
            except sel_exc.ElementNotInteractableException:
                print('not_interactable_day')
                pass

        self.driver.find_element_by_id(self.go_button_id).click()
        self.score_chart_wait(station_name)
        self.screenshot('done')
