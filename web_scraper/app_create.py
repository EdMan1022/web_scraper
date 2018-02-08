from flask import Flask
from .extensions import db
import fulcrum_reconciliation.exceptions as exc
from fulcrum_reconciliation.blueprints import survey_management_bp


def create_app(config):

    if config is None:
        raise exc.NoAppConfigError

    app = Flask(config.APP_NAME)
    app.config.from_object(config)

    db.init_app(app)
    app.register_blueprint(survey_management_bp)

    db.app = app
    return app
