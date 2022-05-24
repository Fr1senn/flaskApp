from flask import Blueprint, render_template, redirect, session, url_for, request, flash
import psycopg2 as pg

from . import connect_and_select, connect_and_iud
import website.models as models

admin = Blueprint('admin', __name__)

status = {
    'Тренер': 1,
    'Администратор': 2,
    'Управляющий': 3,
    'Клиент': 4
}


@admin.route('/')
def home():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    return render_template('admin/admin_base.html')


@admin.route('/users')
def users():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_select(f'''
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
    user = connect_and_select(f'''
        SELECT *
        FROM public.user
        JOIN status ON status.id = status_id
        WHERE public.user.id = {user_id};
    ''', user=session['email'].split('@')[0], password=session['password'])
    status_list = connect_and_select('''SELECT title FROM status''')
    if request.method == 'POST':
        action = request.form.get('action').capitalize()
        conn = pg.connect(dbname='fitclub', user=session['email'].split('@')[0], password=session['password'])
        cursor = conn.cursor()
        if action == 'Удалить':
            cursor.execute(f'''DELETE FROM public.user WHERE id = {user_id}''')
            conn.commit()
            return redirect(url_for('admin.users'))
        if action == 'Изменить':
            cursor.execute(f'''
                UPDATE public.user SET first_name = '{request.form['first_name']}' WHERE id = {user_id};
                UPDATE public.user SET last_name = '{request.form['last_name']}' WHERE id = {user_id};
                UPDATE public.user SET email = '{request.form['email']}' WHERE id = {user_id};
                UPDATE public.user SET birthday = '{request.form['birthday']}' WHERE id = {user_id};
                UPDATE public.user SET status_id = {status[request.form['status']]} WHERE id = {user_id};
            ''')
            conn.commit()
            return redirect(url_for('admin.users'))
    return render_template('admin/crud/user_crud/user_crud.html', user=user, status=status_list)


@admin.route('/users/add', methods=['POST', 'GET'])
def user_crud_add():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    status_list = connect_and_select('''SELECT title FROM status''')
    if request.method == 'POST':
        connect_and_iud(f'''
            INSERT INTO public.user(first_name, last_name, email, birthday, status_id)
            VALUES('{request.form['first_name']}', '{request.form['last_name']}', '{request.form['email']}', '{request.form['birthday']}', {status[request.form['status']]})
        ''')
        connect_and_iud(f'''
            CREATE ROLE {request.form['email'].split('@')[0]} WITH LOGIN PASSWORD '{request.form['email'].split('@')[0]}';
        ''')
        if request.form['status'] == 'Клиент':
            connect_and_iud(f'''
                GRANT authenticated_user TO {request.form['email'].split('@')[0]}
            ''')
        if request.form['status'] == 'Тренер':
            connect_and_iud(f'''
                GRANT coach TO {request.form['email'].split('@')[0]}
            ''')
        if request.form['status'] == 'Администратор':
            connect_and_iud(f'''
                GRANT administrator TO {request.form['email'].split('@')[0]}
            ''')
        if request.form['status'] == 'Управляющий':
            connect_and_iud(f'''
                GRANT manager TO {request.form['email'].split('@')[0]}
            ''')
        flash(
            f"Пользователь успешно создан! Данные для входа {request.form['email']} | {request.form['email'].split('@')[0]}",
            category='error')
        return redirect(url_for('admin.users'))
    return render_template('admin/crud/user_crud/user_crud_add.html', status_list=status_list)


@admin.route('/reviews')
def reviews():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    review_list = connect_and_select('''
        SELECT review.id, first_name, last_name, text, date
        FROM public.user
        JOIN review ON user_id = public.user.id;''', user=session['email'].split('@')[0], password=session['password'])
    return render_template('admin/reviews.html', reviews=review_list)


@admin.route('/user_progress')
def user_progress():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_progress_list = connect_and_select('''
        SELECT first_name, last_name, email, date, value, unit
        FROM public.user
        JOIN user_progress ON user_id = public.user.id
        JOIN unit ON unit.id = unit_id''', user=session['email'].split('@')[0], password=session['password'])
    return render_template('admin/user_progress.html', user_progress=user_progress_list)


@admin.route('/user_schedule')
def user_schedule():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_schedule_list = connect_and_select('''
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
    user_post_list = connect_and_select('''
        SELECT user_post.id, first_name, last_name, date, salary, title
        FROM status
        JOIN public.user ON status_id = status.id
        JOIN user_post ON user_id = public.user.id;''', user=session['email'].split('@')[0],
                                        password=session['password'])
    return render_template('admin/user_post.html', user_post=user_post_list)


@admin.route('/user_post/<int:user_post_id>', methods=['POST', 'GET'])
def user_post_crud(user_post_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_select(f'''
        SELECT public.user.id, first_name, last_name, title, status_id
        FROM status
        JOIN public.user ON status_id = status.id
        JOIN user_post ON user_id = public.user.id
        WHERE status_id != 4 AND user_post.id = {user_post_id};
    ''', user=session['email'].split('@')[0], password=session['password'])
    post_list = connect_and_select('''SELECT * FROM status''', user=session['email'].split('@')[0],
                                   password=session['password'])
    user_post_list = connect_and_select(f'''
        SELECT user_post.id, public.user.id, status.id, salary
        FROM status
        JOIN public.user ON status_id = status.id
        JOIN user_post ON user_id = public.user.id
        WHERE user_post.id = {user_post_id}''', user=session['email'].split('@')[0], password=session['password'])
    if request.method == 'POST':
        if request.form['action'] == 'Удалить':
            connect_and_iud(f'''DELETE FROM user_post WHERE id = {user_post_id}''', user=session['email'].split('@')[0],
                            password=session['password'])
            return redirect(url_for('admin.user_post'))
        if request.form['action'] == 'Изменить':
            post_dict = {}
            for item in post_list:
                post_dict[item[1]] = item[0]
            connect_and_iud(f'''
                UPDATE public.user SET status_id = {post_dict[request.form['status_id']]} WHERE public.user.id = (SELECT user_id FROM user_post WHERE id = {user_post_id});
                UPDATE user_post SET salary = {request.form['salary']} WHERE id = {user_post_id}
            ''', user=session['email'].split('@')[0], password=session['password'])
            return redirect(url_for('admin.user_post'))
    return render_template('admin/crud/user_post_crud/user_post_crud.html', user_list=user_list, post_list=post_list,
                           user_post_list=user_post_list)


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
                                                         user=session['email'].split('@')[0],
                                                         password=session['password'])
    return render_template('admin/user_subscription_duration.html',
                           user_subscription_duration=user_subscription_duration_list)


@admin.route('/user_training_schedule_attendance')
def user_training_schedule_attendance():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_training_schedule_attendance_list = connect_and_select('''
        SELECT first_name, last_name, attendance, title
        FROM public.user
        JOIN user_training_schedule_attendance ON user_id = public.user.id
        JOIN attendance ON attendance.id = attendance_id
        JOIN training_schedule_equipment ON training_schedule_equipment.id = training_schedule_equipment_id
        JOIN equipment ON equipment.id = equipment_id''', user=session['email'].split('@')[0],
                                                                password=session['password'])
    return render_template('admin/user_training_schedule_attendance.html',
                           user_training_schedule_attendance=user_training_schedule_attendance_list)
