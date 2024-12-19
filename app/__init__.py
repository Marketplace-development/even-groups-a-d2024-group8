import base64
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def b64encode(value):
    if value:
        return base64.b64encode(value).decode('utf-8')
    return None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from .models import Profile, Musician, Soloist, Band, Venue
        db.create_all()

        from .routes import main
        app.register_blueprint(main)

        app.jinja_env.filters['b64encode'] = b64encode

    return app