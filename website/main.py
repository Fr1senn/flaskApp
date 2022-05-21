from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from environ import Env
import sqlalchemy as sql

import psycopg2 as pg

main = Blueprint('main', __name__)

env = Env()
env.read_env()


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/reviews')
def reviews():
    return render_template('reviews.html')


@main.route('/subscription')
def subscription():
    return render_template('subscriptions.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@main.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        engine = sql.create_engine(f"postgresql+psycopg2://postgres:admin@localhost/{env('DB_NAME')}")

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
    return render_template('registration.html')
