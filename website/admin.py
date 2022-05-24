from flask import Blueprint, render_template, redirect, session, url_for, request
import psycopg2 as pg

from . import connect_and_execute_query
import website.models as models

admin = Blueprint('admin', __name__)


@admin.route('/')
def home():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    return render_template('admin/admin_base.html')


@admin.route('/users')
def users():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_execute_query(f'''
        SELECT public.user.id, first_name, last_name, email, birthday, registration_date, title
        FROM public.user
        JOIN status ON status.id = status_id
        ORDER BY public.user.id;
    ''', user=session['email'].split('@')[0], password=session['password'])
    return render_template('admin/users.html', users=user_list)


@admin.route('/users/<int:user_id>', methods=['POST', 'GET'])
def user_crud(user_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user = connect_and_execute_query(f'''
        SELECT *
        FROM public.user
        JOIN status ON status.id = status_id
        WHERE public.user.id = {user_id};
    ''', user=session['email'].split('@')[0], password=session['password'])
    status_list = connect_and_execute_query('''SELECT title FROM status''')
    if request.method == 'POST':
        action = request.form.get('action').capitalize()
        conn = pg.connect(dbname='fitclub', user=session['email'].split('@')[0], password=session['password'])
        cursor = conn.cursor()
        if action == 'Удалить':
            cursor.execute(f'''DELETE FROM public.user WHERE id = {user_id}''')
            conn.commit()
            return redirect(url_for('admin.users'))
        if action == 'Изменить':
            status = {
                'Тренер': 1,
                'Администратор': 2,
                'Управляющий': 3,
                'Клиент': 4
            }
            cursor.execute(f'''
                UPDATE public.user SET first_name = '{request.form['first_name']}' WHERE id = {user_id};
                UPDATE public.user SET last_name = '{request.form['last_name']}' WHERE id = {user_id};
                UPDATE public.user SET email = '{request.form['email']}' WHERE id = {user_id};
                UPDATE public.user SET birthday = '{request.form['birthday']}' WHERE id = {user_id};
                UPDATE public.user SET status_id = '{status[request.form['status']]}' WHERE id = {user_id};
            ''')
            conn.commit()
            return redirect(url_for('admin.users'))
    return render_template('admin/crud/user_crud.html', user=user, status=status_list)


@admin.route('/reviews')
def reviews():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    review_list = connect_and_execute_query('''
    SELECT first_name, last_name, email, text, date
    FROM public.user
    JOIN review ON user_id = public.user.id;''', user=session['email'].split('@')[0], password=session['password'])
    return render_template('admin/reviews.html', reviews=review_list)


@admin.route('/user_progress')
def user_progress():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_progress_list = connect_and_execute_query('''
        SELECT first_name, last_name, email, date, value, unit
        FROM public.user
        JOIN user_progress ON user_id = public.user.id
        JOIN unit ON unit.id = unit_id''', user=session['email'].split('@')[0], password=session['password'])
    return render_template('admin/user_progress.html', user_progress=user_progress_list)


@admin.route('/user_schedule')
def user_schedule():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_schedule_list = connect_and_execute_query('''
        SELECT first_name, last_name, date, duration
        FROM public.user
        JOIN user_schedule ON user_id = public.user.id
        JOIN schedule ON schedule.id = schedule_id''', user=session['email'].split('@')[0],
                                                   password=session['password'])
    return render_template('admin/user_schedule.html', user_schedule=user_schedule_list)


@admin.route('/user_post')
def user_post():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_post_list = connect_and_execute_query('''
        SELECT first_name, last_name, date, salary, title
        FROM status
        JOIN public.user ON status_id = status.id
        JOIN user_post ON user_id = public.user.id;''', user=session['email'].split('@')[0], password=session['password'])
    return render_template('admin/user_post.html', user_post=user_post_list)


@admin.route('/user_subscription_duration')
def user_subscription_duration():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_subscription_duration_list = connect_and_execute_query('''
        SELECT first_name, last_name, title, duration, date, price
        FROM public.user
        JOIN user_subscription_duration ON user_id = public.user.id
        JOIN subscription ON subscription.id = subscription_id
        JOIN subscription_duration ON subscription_duration.id = subscription_duration_id''',
                                                                user=session['email'].split('@')[0],
                                                                password=session['password'])
    return render_template('admin/user_subscription_duration.html',
                           user_subscription_duration=user_subscription_duration_list)


@admin.route('/user_training_schedule_attendance')
def user_training_schedule_attendance():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_training_schedule_attendance_list = connect_and_execute_query('''
        SELECT first_name, last_name, attendance, title
        FROM public.user
        JOIN user_training_schedule_attendance ON user_id = public.user.id
        JOIN attendance ON attendance.id = attendance_id
        JOIN training_schedule_equipment ON training_schedule_equipment.id = training_schedule_equipment_id
        JOIN equipment ON equipment.id = equipment_id''', user=session['email'].split('@')[0],
                                                                       password=session['password'])
    return render_template('admin/user_training_schedule_attendance.html',
                           user_training_schedule_attendance=user_training_schedule_attendance_list)
