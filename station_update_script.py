from manage import app
import datetime
import pandas as pd
from web_scraper.classes.web_crawler import WebCrawler, DayPart
import os

ctx = app.test_request_context()
ctx.push()


web_crawler = WebCrawler()
web_crawler.login()

start_date = datetime.datetime(day=25, month=1, year=2018)
end_date = datetime.datetime(day=31, month=1, year=2018)
day_part = DayPart(start_time="6:00 AM", end_time="7:00 PM", days=True)

stations = os.environ['STATION_LIST'].split(',')[::-1]

for station in stations:
    print(station)
    try:
        web_crawler.update_station_trends(station, start_date, end_date, day_part)
    except Exception as e:
        pd.DataFrame.from_dict(web_crawler.station_averages, 'index').to_csv('averages_update.csv')
        web_crawler.driver.close()
        raise e

pd.DataFrame.from_dict(web_crawler.station_averages, 'index').to_csv('averages_update.csv')
