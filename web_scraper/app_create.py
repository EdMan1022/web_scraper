from flask import Flask
from .extensions import db
from .blueprints import react_bp


def create_app(config):

    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    app.register_blueprint(react_bp)

    db.app = app

    return app
