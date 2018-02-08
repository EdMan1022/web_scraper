from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from fulcrum_reconciliation.config import ProductionConfig
from fulcrum_reconciliation.create_app import create_app

app = create_app(config=ProductionConfig)

from web_scraper.extensions import db

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
