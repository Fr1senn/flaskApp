from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from environ import Env
from datetime import datetime

from . import connect_and_select, connect_and_iud

main = Blueprint('main', __name__)

env = Env()
env.read_env()


@main.route('/')
def home():
    user_list = connect_and_select('''
        SELECT first_name, last_name, title
        FROM public.user
        JOIN status ON status.id = status_id
        WHERE status_id = 1 OR status_id = 2;
    ''')
    return render_template('index.html', user_list=user_list)


@main.route('/reviews', methods=['GET', 'POST'])
def reviews():
    review = connect_and_select('''
        SELECT first_name, last_name, date, text
        FROM public.user
        JOIN review ON review.user_id = public.user.id;
    ''')
    if request.method == 'POST':
        text = request.form.get('text')
        if len(text) == 0:
            flash('Введите сообщение!', category='error')
            return redirect(url_for('main.reviews'))
        connect_and_iud(f'''
            INSERT INTO review(text, user_id) VALUES('{text}', {session['user_id']})
        ''', user=session['username'], password=session['password'])
        return redirect(url_for('main.home'))
    return render_template('reviews.html', reviews=review)


@main.route('/subscription', methods=['GET', 'POST'])
def subscription():
    subs_list = connect_and_select('''
        SELECT *
        FROM subscription
        WHERE id != 0;
    ''')
    subs_duration_list = connect_and_select('''
        SELECT * FROM subscription_duration WHERE id != 0;
    ''')
    if request.method == 'POST':
        if not session['logged_in']:
            return redirect(url_for('main.login'))
        if str(request.form.get('sub')) == '---':
            flash('Необходимо выбрать абонемент!', category='error')
            return redirect(url_for('main.subscription'))
        elif str(request.form.get('sub_duration')) == '---':
            flash('Необходимо выбрать длительность абонемента!', category='error')
            return redirect(url_for('main.subscription'))
        else:
            subs_dict = {}
            subs_dur_dict = {}
            price = float(request.form['sub'].split()[1]) * int(request.form['sub_duration'].split(',')[0].split()[0])
            for item in subs_list:
                subs_dict[item[1]] = item[0]
            for item in subs_duration_list:
                subs_dur_dict[str(item[1])] = item[0]
            connect_and_iud(f'''
                INSERT INTO user_subscription_duration(price, user_id, subscription_id, subscription_duration_id)
                VALUES({price}, {session['user_id']}, {subs_dict[request.form['sub'].split()[0]]}, {subs_dur_dict[request.form['sub_duration']]})
            ''', user=session['username'], password=session['password'])
            return redirect(url_for('profile.home'))
    return render_template('subscriptions.html', subs=subs_list, subs_dur=subs_duration_list)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = connect_and_select(f'''
            SELECT public.user.id, title
            FROM public.user
            JOIN status ON status.id = status_id
            WHERE username = '{username}';
        ''')
        username_list = [item[0] for item in connect_and_select('''SELECT username FROM public.user''')]
        if user is None:
            flash('Пользователь не сущесвует!', category='error')
            return redirect(url_for('main.login'))
        if username not in username_list:
            flash('Неверный логин!', category='error')
            return redirect(url_for('main.login'))
        if password not in psw_list:
            flash('Неверный пароль!', category='error')
            return redirect(url_for('main.login'))
        session['logged_in'] = True
        session['username'] = username
        session['password'] = password
        session['user_id'] = user[0][0]
        session['status'] = user[0][1]
        return redirect(url_for('main.home'))
    return render_template('login.html')


@main.route('/logout')
def logout():
    session['logged_in'] = False
    session['status'] = 'Гость'
    session.pop('username')
    session.pop('password')
    session.pop('user_id')
    return redirect(url_for('main.login'))


psw_list = ['russel', 'toto', 'zhukov', 'barshova']


@main.route('/registration', methods=['GET', 'POST'])
def registration():
    if session['logged_in']:
        return redirect(url_for('profile.home'))
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        birthday = request.form.get('birthday')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if len(first_name) == 0:
            flash('Введите имя!', category='error')
            return redirect(url_for('main.registration'))
        elif len(last_name) == 0:
            flash('Введите фамилию!', category='error')
            return redirect(url_for('main.registration'))
        elif len(birthday) == 0:
            flash('Введите дату рождения!', category='error')
            return redirect(url_for('main.registration'))
        elif birthday > datetime.now().strftime('%Y-%m-%d'):
            flash('Некорректная дата рождения!', category='error')
            return redirect(url_for('main.registration'))
        elif password != password_confirm:
            flash('Пароли не совпадают!', category='error')
            return redirect(url_for('main.registration'))
        elif '@' not in request.form['email'] or '.' not in request.form['email']:
            flash('Некорректный email!', category='error')
            return redirect(url_for('main.registration'))
        else:
            connect_and_iud(f'''CREATE ROLE {username} WITH LOGIN PASSWORD '{password}';''')
            connect_and_iud(f'''
                INSERT INTO public.user(first_name, last_name, username, birthday, email)
                VALUES('{first_name}', '{last_name}', '{username}', '{birthday}', '{request.form['email']}');
            ''')
            connect_and_iud(f'''GRANT authenticated_user TO {username}''')
            psw_list.append(password)
            return redirect(url_for('main.login'))
    return render_template('registration.html')
