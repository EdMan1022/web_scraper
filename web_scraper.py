from web_scraper.app_create import create_app
from web_scraper.config import DevelopmentConfig

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run()
