from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import traceback


# instantiating application support objects
db = SQLAlchemy()
mail = Mail()
cors = CORS()
migrate = Migrate(compare_type=True)


def create_app():
    """Construct the core application."""

    app = Flask(__name__, instance_relative_config=False,
                static_url_path='/static')
    # The specific configuration class will depend on the value stored in the APP_SETTINGS
    # environment variable. If the variable is undefined, the configuration will fall back
    # to DevelopmentConfig by default.
    env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
    app.config.from_object(env_config)

    # Enable Cross Origin Resource Sharing
    # CORS(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})

    jwt = JWTManager(app)

    mail.init_app(app)

    # database migrations
    migrate.init_app(app, db)
    db.init_app(app)

    with app.app_context():
        # import models
        from .models import (Token
                             )

        # Import controller blueprints
        '''Controller blueprints'''
        # from .controllers.auth import auth_bp, create_default_user
        

        # Register Blueprints
        '''registered blueprints'''
        # app.register_blueprint(auth_bp)
        

        # revoke tokens
        @jwt.token_in_blocklist_loader
        def check_if_token_is_revoked(jwt_header, jwt_payload):
            jti = jwt_payload["jti"]
            token = db.session.query(
                Token.RevokedTokenModel.id).filter_by(jti=jti).scalar()
            return token is not None

        # return flask object with all configuration settings
        return app
