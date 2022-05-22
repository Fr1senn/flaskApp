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
    if not session['logged_in']:
        return redirect(url_for('main.login'))
    email = session['email']
    password = session['password']
    engine = sql.create_engine(f"postgresql+psycopg2://{email.split('@')[0]}:{password}@localhost/{env('DB_NAME')}")
    user = engine.execute(f"SELECT * FROM public.user WHERE email = '{email}'").fetchone()
    return render_template('profile.html', user=user)


@main.route('/reviews', methods=['GET', 'POST'])
def reviews():
    email = session['email']
    password = session['password']
    engine = sql.create_engine(f"postgresql+psycopg2://{email.split('@')[0]}:{password}@localhost/{env('DB_NAME')}")
    if request.method == 'POST':
        text = request.form.get('text')
        user = engine.execute(f"SELECT * FROM public.user WHERE email = '{email}'").fetchone()
        if len(text) == 0:
            flash('Введите сообщение!', category='error')
            return redirect(url_for('main.reviews'))
        new_review = models.Review(text=text, user_id=user[0])
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('main.home'))
    reviews = engine.execute('''
        SELECT public.user.id, first_name, last_name, "date", "text"
        FROM public.user
        JOIN review ON review.user_id = public.user.id
    ''')
    return render_template('reviews.html', reviews=reviews)


@main.route('/subscription')
def subscription():
    return render_template('subscriptions.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        engine = sql.create_engine(f"postgresql+psycopg2://guest:guest@localhost/{env('DB_NAME')}")
        user = engine.execute(f"SELECT * FROM public.user WHERE email = '{email}'").fetchone()
        if user is None:
            flash('Пользователь не сущесвует!', category='error')
            return redirect(url_for('main.login'))
        session['logged_in'] = True
        session['email'] = email
        session['password'] = password
        session['user_id'] = user[0]
        return redirect(url_for('main.home'))
    return render_template('login.html')


@main.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('email')
    session.pop('password')
    session.pop('user_id')
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
            new_user = models.User(first_name=first_name.capitalize().strip(),
                                   last_name=last_name.capitalize().strip(),
                                   email=email.strip(), birthday=birthday,
                                   status='клиент')
            db.session.add(new_user)
            db.session.commit()
            flash('Аккаунт успешно создан!', category='success')
            return redirect(url_for('main.login'))

    return render_template('registration.html')
