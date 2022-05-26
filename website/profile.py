from flask import Blueprint, session, redirect, render_template, url_for
from environ import Env

from . import connect_and_select

profile = Blueprint('profile', __name__)

env = Env()
env.read_env()


@profile.route('/')
def home():
    if not session['logged_in']:
        return redirect(url_for('main.login'))
    user = connect_and_select(f'''
        SELECT DISTINCT id, first_name, last_name, birthday, registration_date, unit, LAST_VALUE(value) OVER(PARTITION BY unit)
        FROM get_user_info('{session['username']}')
    ''', user=session['username'], password=session['password'])
    return render_template('profile/profile_base.html', user=user)


@profile.route('/purchases')
def purchases():
    if not session['logged_in']:
        return redirect(url_for('main.login'))
    user = connect_and_select(f'''
            SELECT DISTINCT id, first_name, last_name, birthday, registration_date, unit, LAST_VALUE(value) OVER(PARTITION BY unit)
            FROM get_user_info('{session['username']}')
        ''', user=session['username'], password=session['password'])
    purchase_list = connect_and_select(f'''
           SELECT first_name, last_name, price, date, title, duration
           FROM public.user
           JOIN user_subscription_duration ON user_id = public.user.id
           JOIN subscription ON subscription.id = subscription_id
           JOIN subscription_duration ON subscription_duration.id = subscription_duration_id
           WHERE username = '{session['username']}';
       ''', user=session['username'], password=session['password'])
    return render_template('profile/purchases.html', user=user, purchase_list=purchase_list)


@profile.route('/attendance')
def attendance():
    if not session['logged_in']:
        return redirect(url_for('main.login'))
    user = connect_and_select(f'''
            SELECT DISTINCT id, first_name, last_name, birthday, registration_date, unit, LAST_VALUE(value) OVER(PARTITION BY unit)
            FROM get_user_info('{session['username']}')
        ''', user=session['username'], password=session['password'])
    attendance_list = connect_and_select(f'''
        SELECT first_name, last_name, attendance
        FROM public.user
        JOIN user_training_schedule_attendance ON user_training_schedule_attendance.user_id = public.user.id
        JOIN attendance ON attendance.id = attendance_id
        WHERE username = '{session['username']}';
    ''', user=session['username'], password=session['password'])
    return render_template('profile/attendance.html', user=user, attendance_list=attendance_list)


@profile.route('/measurements')
def measurements():
    if not session['logged_in']:
        return redirect(url_for('main.login'))
    user = connect_and_select(f'''
            SELECT DISTINCT id, first_name, last_name, birthday, registration_date, unit, LAST_VALUE(value) OVER(PARTITION BY unit)
            FROM get_user_info('{session['username']}')
        ''', user=session['username'], password=session['password'])
    measerement_list = connect_and_select(f'''
        SELECT first_name, last_name, value, unit, date
        FROM public.user
        JOIN user_progress ON user_progress.user_id = public.user.id
        JOIN unit ON unit.id = unit_id
        WHERE username = '{session['username']}';
    ''', user=session['username'], password=session['password'])
    return render_template('profile/measurements.html', user=user, measerement_list=measerement_list)
