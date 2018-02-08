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

    input_pause_time = .5
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
            buttonset_list = self.driver.find_elements_by_class_name(self.station_window_button_class)
            buttonset = [element for element in buttonset_list if element.text == self.buttonset_text][0]

            buttons = buttonset.find_elements_by_tag_name(self.button_tag)
            ok_button = [element for element in buttons if element.text == self.ok_text][0]

            ok_button.click()
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
        element_list = station_window.find_elements_by_xpath(self.station_match_text.format(station_name,
                                                                                            station_name))
        reduced_element_list = [element for element in element_list if element.text == station_name]
        station_element = reduced_element_list[0]
        station_element.click()
        self.click_select_ok()

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
        year_select = self.date_picker_ui.find_element_by_class(self.datepicker_year_class)
        self.select_find(year_select, str(year))

    def select_month(self, month):
        month_select = self.date_picker_ui.find_element_by_class(self.datepicker_month_class)
        options = month_select.find_elements_by_tag_name('option')
        select_option = [
            option_element for option_element in options if option_element.get_property('value') == str(month-1)][0]
        select_option.click()

    def select_day(self, day):
        datepicker_calendar = self.date_picker_ui.find_element_by_class_name(self.datepicker_calendar_class)
        date_links = datepicker_calendar.find_elements_by_tag_name('a')
        date_link = [this_date for this_date in date_links if this_date.text == str(day)][0]
        date_link.click()

    def select_time_range(self, time_start, time_end):
        time_range_element = self.driver.find_element_by_id(self.time_range_id)
        time_range_buttons = time_range_element.find_elements_by_tag_name(self.button_tag)
        start_button = time_range_buttons[0]
        end_button = time_range_buttons[1]
        self.button_click(start_button)
        self.select_date(time_start)

        self.button_click(end_button)
        self.select_date(time_end)

    def show_average(self):
        self.driver.find_element_by_class_name(self.average_overlay_name)
        average_check = self.driver.find_elements_by_class_name(self.average_check_class)
        if len(average_check) == 0:
            average_check = self.driver.find_elements_by_class_name(self.average_class_name)[0]
            average_check.find_element_by_tag_name('input').click()

    def record_average(self, station_name):
        average_overlay = self.driver.find_element_by_class_name(self.average_overlay_name)
        average_texts = average_overlay.find_elements_by_tag_name(self.tspan_name)

        average_text_element = [avg_text for avg_text in average_texts if self.average_text_match in avg_text.text][0]
        average_text = average_text_element.text
        average_text.replace(self.average_text_match, '')
        self.station_averages[station_name] = average_text

    def select_day_part(self, day_part: DayPart):
        sidebar = self.driver.find_element_by_id(self.report_sidebar)
        daypart_filter = sidebar.find_elements_by_class_name('report-filter-item')[-2]
        daypart_button = daypart_filter.find_elements_by_tag_name(self.button_tag)[0]

        self.button_click(daypart_button)

        daypart_ui = self.driver.find_element_by_id(self.daypart_id)
        daypart_rows = daypart_ui.find_elements_by_tag_name(self.row_tag)

        for row in daypart_rows:
            columns = row.find_elements_by_tag_name(self.column_tag)

            if columns[1].text == day_part.time_range():
                if columns[2].text == day_part.day_text():
                    break

        row.click()
        self.click_select_ok()

    def update_station_trends(self, station_name: str, time_start, time_end,
                              day_part: DayPart):
        self.driver.get(self.audience_reaction_url)
        self.select_station(station_name)
        self.select_time_range(time_start, time_end)
        self.select_day_part(day_part)

        self.driver.find_element_by_id(self.go_button_id).click()

        wait = True

        while wait:
            print('Waiting')
            time.sleep(3)
            average_panel = self.driver.find_elements_by_class_name(self.average_class_name)
            if len(average_panel > 0):
                wait = False

        self.show_average()
        self.record_average(station_name)
