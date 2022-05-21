from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from environ import Env

from .admin import admin
from .main import main

db = SQLAlchemy()
env = Env()
env.read_env()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = env('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://postgres:admin@localhost/{env('DB_NAME')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    import website.models as models

    migrate = Migrate(app, db)

    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(main, url_prefix='/')

    return app
