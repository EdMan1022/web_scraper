from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from web_scraper.config import DevelopmentConfig
from web_scraper.app_create import create_app

app = create_app(config=DevelopmentConfig)

from web_scraper.extensions import db

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
