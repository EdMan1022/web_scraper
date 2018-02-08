from flask import Flask
from .extensions import db


def create_app(config):

    app = Flask(config.APP_NAME)
    app.config.from_object(config)

    db.init_app(app)

    db.app = app

    return app
