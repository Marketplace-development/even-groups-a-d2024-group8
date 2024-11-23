from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config  # This ensures the Config is imported correctly

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)  # Use __name__ instead of a hard-coded string
    app.config.from_object(Config)  # Directly use the Config class

    db.init_app(app)

    with app.app_context():
        from .models import Profile, Musician, Soloist, Band, Venue
        db.create_all()  # Create database tables

        from .routes import main
        app.register_blueprint(main)

    return app
