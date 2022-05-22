from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from environ import Env
import sqlalchemy as sql
import psycopg2 as pg

from . import connect_and_execute_query
from . import models as models
from . import db

main = Blueprint('main', __name__)

env = Env()
env.read_env()


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/reviews', methods=['GET', 'POST'])
def reviews():
    result = connect_and_execute_query('''
        SELECT first_name, last_name, date, text
        FROM public.user
        JOIN review ON review.user_id = public.user.id;
    ''')
    if request.method == 'POST':
        text = request.form.get('text')
        user = connect_and_execute_query(f"SELECT * FROM public.user WHERE email = '{session['email']}'",
                                         user=session['email'].split('@')[0], password=session['password'])
        if len(text) == 0:
            flash('Введите сообщение!', category='error')
            return redirect(url_for('main.reviews'))
        new_review = models.Review(text=text, user_id=user[0])
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('reviews.html', reviews=result)


@main.route('/subscription', methods=['GET', 'POST'])
def subscription():
    if not session['logged_in']:
        return redirect(url_for('main.registration'))
    subs_list = connect_and_execute_query('''
        SELECT title FROM subscription;
    ''', user=session['email'].split('@')[0], password=session['password'])
    subs_duration_list = connect_and_execute_query('''
        SELECT duration FROM subscription_duration;
    ''', user=session['email'].split('@')[0], password=session['password'])
    if request.method == 'POST':
        if str(request.form.get('sub')) == '---':
            flash('Необходимо выбрать абонемент!', category='error')
            return redirect(url_for('main.subscription'))
        elif str(request.form.get('sub_duration')) == '---':
            flash('Необходимо выбрать длительность абонемента!', category='error')
            return redirect(url_for('main.subscription'))
        else:
            sub_id = connect_and_execute_query(f'''
                SELECT id FROM subscription WHERE title = '{request.form.get('sub')}'
            ''', user=session['email'].split('@')[0], password=session['password'])
            sub_dur_id = connect_and_execute_query(f'''
                SELECT id FROM subscription_duration WHERE duration = '{request.form.get('sub_duration')}'
            ''', user=session['email'].split('@')[0], password=session['password'])
            user_subs_dur = models.UserSubscriptionDuration(user_id=session['user_id'],
                                                            subscription_id=sub_id[0],
                                                            subscription_duration_id=sub_dur_id[0],
                                                            price=len(str(request.form.get('sub'))) * int(
                                                                request.form.get('sub_duration').split(',')[0].split(
                                                                    ' ')[0]))
            db.session.add(user_subs_dur)
            db.session.commit()
            return redirect(url_for('profile.home'))
    return render_template('subscriptions.html', subs=subs_list, subs_dur=subs_duration_list)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = connect_and_execute_query(f'''
            SELECT * FROM public.user WHERE email = '{email}'
        ''')
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
    if session['logged_in']:
        return redirect(url_for('profile.home'))
    if request.method == 'POST':
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
            connect_and_execute_query(
                f"CREATE ROLE {email.split('@')[0]} WITH LOGIN PASSWORD '{password}'")
            connect_and_execute_query(f"GRANT authenticated_user TO {email.split('@')[0]}")
            new_user = models.User(first_name=first_name.capitalize().strip(),
                                   last_name=last_name.capitalize().strip(),
                                   email=email.strip(), birthday=birthday,
                                   status='клиент')
            db.session.add(new_user)
            db.session.commit()
            flash('Аккаунт успешно создан!', category='success')
            return redirect(url_for('main.login'))
    return render_template('registration.html')
