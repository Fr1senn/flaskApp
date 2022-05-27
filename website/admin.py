from flask import Blueprint, render_template, redirect, session, url_for, request, flash
import psycopg2 as pg

from . import connect_and_select, connect_and_iud
import website.models as models

admin = Blueprint('admin', __name__)


@admin.route('/')
def home():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    total_inc = connect_and_select(f'''
        WITH month_list AS(
            SELECT ml FROM generate_series(1, 12) AS ml),
        d AS(
            SELECT DISTINCT ml,
            SUM(COALESCE(price, 0)) OVER(PARTITION BY ml) AS monthly_income
            FROM month_list
            LEFT JOIN user_subscription_duration ON ml = EXTRACT(MONTH FROM date)
            ORDER BY ml)
        SELECT SUM(monthly_income) FROM d;
    ''', user=session['username'], password=session['password'])
    rank = connect_and_select(f'''
        WITH d AS(
            SELECT *
            FROM user_subscription_duration
            JOIN subscription ON subscription.id = subscription_id
            JOIN subscription_duration ON subscription_duration.id = subscription_duration_id)
        SELECT title,
        DENSE_RANK() OVER(ORDER BY COUNT(user_id) DESC) AS pop_subs,
        DENSE_RANK() OVER(ORDER BY AVG(duration) DESC) AS avg_dur
        FROM d
        GROUP BY title LIMIT 1;
    ''', user=session['username'], password=session['password'])
    return render_template('admin/admin_base.html', total_inc=total_inc, pop_sub=rank)


@admin.route('/users')
def users():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_select(f'''
        SELECT public.user.id, first_name, last_name, username, birthday, registration_date, title
        FROM public.user
        JOIN status ON status.id = status_id
        WHERE public.user.id != 0
        ORDER BY public.user.id;
    ''', user=session['username'], password=session['password'])
    return render_template('admin/users.html', users=user_list)


@admin.route('/reviews')
def reviews():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    review_list = connect_and_select('''
        SELECT review.id, first_name, last_name, text, date
        FROM public.user
        JOIN review ON user_id = public.user.id;''', user=session['username'], password=session['password'])
    return render_template('admin/reviews.html', reviews=review_list)


@admin.route('/user_progress')
def user_progress():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_progress_list = connect_and_select('''
        SELECT DISTINCT public.user.id, first_name, last_name, unit,
        LAST_VALUE(value) OVER(PARTITION BY unit, public.user.id)
        FROM public.user
        JOIN user_progress ON user_id = public.user.id
        JOIN unit ON unit.id = unit_id
        ORDER BY public.user.id''', user=session['username'], password=session['password'])
    return render_template('admin/user_progress.html', user_progress=user_progress_list)


@admin.route('/user_schedule')
def user_schedule():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_schedule_list = connect_and_select('''
        SELECT user_schedule.id, first_name, last_name, date, duration
        FROM public.user
        JOIN user_schedule ON user_id = public.user.id
        JOIN schedule ON schedule.id = schedule_id''', user=session['username'],
                                            password=session['password'])
    return render_template('admin/user_schedule.html', user_schedule=user_schedule_list)


@admin.route('/user_post')
def user_post():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_post_list = connect_and_select('''
        SELECT user_post.id, first_name, last_name, date, salary, title
        FROM status
        JOIN public.user ON status_id = status.id
        JOIN user_post ON user_id = public.user.id;''', user=session['username'], password=session['password'])
    return render_template('admin/user_post.html', user_post_list=user_post_list)


@admin.route('/user_subscription_duration')
def user_subscription_duration():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_subscription_duration_list = connect_and_select('''
        SELECT first_name, last_name, title, duration, date, price
        FROM public.user
        JOIN user_subscription_duration ON user_id = public.user.id
        JOIN subscription ON subscription.id = subscription_id
        JOIN subscription_duration ON subscription_duration.id = subscription_duration_id''',
                                                         user=session['username'],
                                                         password=session['password'])
    return render_template('admin/user_subscription_duration.html',
                           user_subscription_duration=user_subscription_duration_list)


@admin.route('/user_training_schedule_attendance')
def user_training_schedule_attendance():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_training_schedule_attendance_list = connect_and_select('''
        SELECT user_training_schedule_attendance.id, first_name, last_name, date, duration, status
        FROM public.user
        JOIN user_training_schedule_attendance ON user_id = public.user.id
        JOIN training_schedule ON training_schedule.id = training_schedule_id
        JOIN attendance_status ON attendance_status.id = user_training_schedule_attendance.status_id
    ''', user=session['username'], password=session['password'])
    return render_template('admin/user_training_schedule_attendance.html',
                           user_training_schedule_attendance=user_training_schedule_attendance_list)


@admin.route('/subscription_duration')
def subscription_duration():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    subs_dur_list = connect_and_select('''
        SELECT * FROM subscription_duration WHERE id != 0;
    ''', user=session['username'], password=session['password'])
    return render_template('admin/subscription_duration.html', subs_dur_list=subs_dur_list)


@admin.route('/subscription')
def subscription():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    subs_list = connect_and_select('''
        SELECT * FROM subscription WHERE id != 0;
    ''', user=session['username'], password=session['password'])
    return render_template('admin/subscription.html', subs_list=subs_list)
