from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from environ import Env
import psycopg2 as pg

db = SQLAlchemy()
env = Env()
env.read_env()


def connect_and_select(query, dbname='fitclub', user='guest', password='guest'):
    try:
        connection = pg.connect(dbname=dbname, user=user, password=password)
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        connection.commit()
        cursor.close()
        connection.close()
        return result
    except pg.Error as err:
        return err.pgerror


def connect_and_iud(query, dbname='fitclub', user='guest', password='guest'):
    try:
        connection = pg.connect(dbname=dbname, user=user, password=password)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
    except pg.Error as err:
        return err.pgerror


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = env('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://postgres:admin@localhost/{env('DB_NAME')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    import website.models as models

    migrate = Migrate(app, db)

    from .main import main
    from .admin import admin
    from .profile import profile
    from .crud import crud

    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(crud, url_prefix='/admin/crud')
    app.register_blueprint(profile, url_prefix='/profile')
    app.register_blueprint(main, url_prefix='/')
    return app
