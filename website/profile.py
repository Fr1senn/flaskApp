from flask import Blueprint, session, redirect, render_template, url_for
from environ import Env

from . import connect_and_execute_query

profile = Blueprint('profile', __name__)

env = Env()
env.read_env()


@profile.route('/')
def home():
    if not session['logged_in']:
        return redirect(url_for('main.login'))
    user = connect_and_execute_query(f'''
        SELECT public.user.id, first_name, last_name, email, birthday, registration_date, "value", unit
        FROM public.user
        JOIN user_progress ON user_id = public.user.id
        JOIN unit ON unit.id = unit_id
        WHERE email = '{session['email']}';
    ''', user=session['email'].split('@')[0], password=session['password'])
    return render_template('profile/profile.html', user=user)
