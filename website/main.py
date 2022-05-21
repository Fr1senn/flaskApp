from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from environ import Env
import sqlalchemy as sql

from . import models as models
from . import db

main = Blueprint('main', __name__)

env = Env()
env.read_env()


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/profile')
def profile():

    return render_template('profile.html')


@main.route('/reviews')
def reviews():
    return render_template('reviews.html')


@main.route('/subscription')
def subscription():
    return render_template('subscriptions.html')


@main.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        engine = sql.create_engine(f"postgresql+psycopg2://{email.split('@')[0]}:{password}@localhost/{env('DB_NAME')}")
        session['logged_in'] = True
        session['username'] = email.split('@')[0]
        return redirect(url_for('main.home'))
    return render_template('login.html')


@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('main.login'))


@main.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        engine = sql.create_engine(f"postgresql+psycopg2://guest:guest@localhost/{env('DB_NAME')}")

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        birthday = request.form.get('birthday')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if '@' not in email and '.' not in email:
            flash('email некорректен', category='error')
        elif password != password_confirm:
            flash('Пароли не совпадают', category='error')
        else:
            engine.execute(
                f"CREATE ROLE {email.split('@')[0]} WITH LOGIN PASSWORD '{password}'")
            engine.execute(f"GRANT authenticated_user TO {email.split('@')[0]}")
            new_user = models.User(first_name=first_name, last_name=last_name, email=email, birthday=birthday,
                                   status='клиент')
            db.session.add(new_user)
            db.session.commit()
            flash('Аккаунт успешно создан!', category='success')
            return redirect(url_for('main.login'))

    return render_template('registration.html')
