from flask import Blueprint, redirect, render_template, session, request, url_for, flash
import psycopg2 as pg

from website import connect_and_select, connect_and_iud

crud = Blueprint('crud', __name__)

status = {
    'Тренер': 1,
    'Администратор': 2,
    'Управляющий': 3,
    'Клиент': 4
}


@crud.route('/users/<int:user_id>', methods=['POST', 'GET'])
def user_crud(user_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user = connect_and_select(f'''
        SELECT *
        FROM public.user
        JOIN status ON status.id = status_id
        WHERE public.user.id = {user_id};
    ''', user=session['username'], password=session['password'])
    status_list = connect_and_select('''SELECT title FROM status''')
    if request.method == 'POST':
        action = request.form.get('action').capitalize()
        conn = pg.connect(dbname='fitclub', user=session['username'], password=session['password'])
        cursor = conn.cursor()
        if action == 'Удалить':
            cursor.execute(f'''DELETE FROM public.user WHERE id = {user_id}''')
            conn.commit()
            return redirect(url_for('admin.users'))
        if action == 'Изменить':
            cursor.execute(f'''
                UPDATE public.user SET first_name = '{request.form['first_name']}' WHERE id = {user_id};
                UPDATE public.user SET last_name = '{request.form['last_name']}' WHERE id = {user_id};
                UPDATE public.user SET username = '{request.form['username']}' WHERE id = {user_id};
                UPDATE public.user SET birthday = '{request.form['birthday']}' WHERE id = {user_id};
                UPDATE public.user SET status_id = {status[request.form['status']]} WHERE id = {user_id};
            ''')
            conn.commit()
            return redirect(url_for('admin.users'))
    return render_template('admin/crud/user_crud/user_crud.html', user=user, status=status_list)


@crud.route('/users/add', methods=['POST', 'GET'])
def user_crud_add():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    status_list = connect_and_select('''SELECT title FROM status''')
    if request.method == 'POST':
        connect_and_iud(f'''
            INSERT INTO public.user(first_name, last_name, username, birthday, status_id)
            VALUES('{request.form['first_name']}', '{request.form['last_name']}', '{request.form['username']}', '{request.form['birthday']}', {status[request.form['status']]})
        ''')
        connect_and_iud(f'''
            CREATE ROLE {request.form['username']} WITH LOGIN PASSWORD '{request.form['username']}';
        ''')
        if request.form['status'] == 'Клиент':
            connect_and_iud(f'''
                GRANT authenticated_user TO {request.form['username']}
            ''')
        if request.form['status'] == 'Тренер':
            connect_and_iud(f'''
                GRANT coach TO {request.form['username']}
            ''')
        if request.form['status'] == 'Администратор':
            connect_and_iud(f'''
                GRANT administrator TO {request.form['username']}
            ''')
        if request.form['status'] == 'Управляющий':
            connect_and_iud(f'''
                GRANT manager TO {request.form['username']}
            ''')
        flash(
            f"Пользователь успешно создан! Данные для входа {request.form['username']} | {request.form['username']}",
            category='error')
        return redirect(url_for('admin.users'))
    return render_template('admin/crud/user_crud/user_crud_add.html', status_list=status_list)


@crud.route('/user_post/<int:user_post_id>', methods=['POST', 'GET'])
def user_post_crud(user_post_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_select(f'''
        SELECT public.user.id, first_name, last_name, title, status_id
        FROM status
        JOIN public.user ON status_id = status.id
        JOIN user_post ON user_id = public.user.id
        WHERE status_id != 4 AND user_post.id = {user_post_id};
    ''', user=session['username'], password=session['password'])
    post_list = connect_and_select('''SELECT * FROM status''', user=session['username'],
                                   password=session['password'])
    user_post_list = connect_and_select(f'''
        SELECT user_post.id, public.user.id, status.id, salary
        FROM status
        JOIN public.user ON status_id = status.id
        JOIN user_post ON user_id = public.user.id
        WHERE user_post.id = {user_post_id}''', user=session['username'], password=session['password'])
    if request.method == 'POST':
        if request.form['action'] == 'Удалить':
            connect_and_iud(f'''DELETE FROM user_post WHERE id = {user_post_id}''', user=session['username'],
                            password=session['password'])
            return redirect(url_for('admin.user_post'))
        if request.form['action'] == 'Изменить':
            post_dict = {}
            for item in post_list:
                post_dict[item[1]] = item[0]
            connect_and_iud(f'''
                UPDATE public.user SET status_id = {post_dict[request.form['status_id']]} WHERE public.user.id = (SELECT user_id FROM user_post WHERE id = {user_post_id});
                UPDATE user_post SET salary = {request.form['salary']} WHERE id = {user_post_id}
            ''', user=session['username'], password=session['password'])
            return redirect(url_for('admin.user_post'))
    return render_template('admin/crud/user_post_crud/user_post_crud.html', user_list=user_list, post_list=post_list,
                           user_post_list=user_post_list)


@crud.route('/user_post/add', methods=['POST', 'GET'])
def user_post_crud_add():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_select('''
        SELECT public.user.id, first_name, last_name
        FROM public.user
        WHERE status_id = 4;
    ''', user=session['username'], password=session['password'])
    status_list = connect_and_select('''
        SELECT id, title
        FROM status
        WHERE id != 4;
    ''', user=session['username'], password=session['password'])
    if request.method == 'POST':
        user_dict = {}
        status_dict = {}
        for item in user_list:
            user_dict[' '.join([item[1], item[2]])] = item[0]
        for item in status_list:
            status_dict[item[1]] = item[0]
        connect_and_iud(f'''
            UPDATE public.user SET status_id = {status_dict[request.form['status_id']]} WHERE public.user.id = {user_dict[request.form['user_id']]};
            INSERT INTO user_post(user_id, salary)
            VALUES({user_dict[request.form['user_id']]}, {request.form['salary']});
        ''', user=session['username'], password=session['password'])
        return redirect(url_for('admin.user_post'))
    return render_template('admin/crud/user_post_crud/user_post_crud_add.html', user_list=user_list,
                           status_list=status_list)


@crud.route('subscription_duraion/<int:subs_dur_id>', methods=['POST', 'GET'])
def subs_dur_crud(subs_dur_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    subs_dur = connect_and_select(f'''SELECT * FROM subscription_duration WHERE id = {subs_dur_id};''',
                                  user=session['username'], password=session['password'])
    if request.method == 'POST':
        if request.form['action'] == 'Удалить':
            connect_and_iud(f'''DELETE FROM subscription_duration WHERE id = {subs_dur_id}''',
                            user=session['username'], password=session['password'])
            return redirect(url_for('admin.subscription_duration'))
        if request.form['action'] == 'Изменить':
            connect_and_iud(f'''
                UPDATE subscription_duration SET duration = '{request.form['subs_dur']}' WHERE id = {subs_dur_id};
            ''', user=session['username'], password=session['password'])
            return redirect(url_for('admin.subscription_duration'))
    return render_template('admin/crud/subs_dur_crud/subs_dur_crud.html', subs_dur=subs_dur)


@crud.route('subscription_duraion/add', methods=['POST', 'GET'])
def subs_dur_crud_add():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        connect_and_iud(f'''
            INSERT INTO subscription_duration(duration) VALUES('{request.form['subs_dur']} day');
        ''', user=session['username'], password=session['password'])
        return redirect(url_for('admin.subscription_duration'))
    return render_template('admin/crud/subs_dur_crud/subs_dur_crud_add.html')


@crud.route('subscription/<int:subs_id>', methods=['POST', 'GET'])
def subs_crud(subs_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    subs = connect_and_select(f'''SELECT * FROM subscription WHERE id = {subs_id};''',
                              user=session['username'], password=session['password'])
    if request.method == 'POST':
        if request.form['action'] == 'Удалить':
            connect_and_iud(f'''DELETE FROM subscription WHERE id = {subs_id}''', user=session['username'],
                            password=session['password'])
            return redirect(url_for('admin.subscription'))
        if request.form['action'] == 'Изменить':
            connect_and_iud(f'''UPDATE subscription SET title = '{request.form['subs']}' WHERE id = {subs_id}''',
                            user=session['username'], password=session['password'])
            return redirect(url_for('admin.subscription'))
    return render_template('admin/crud/subs_crud/subs_crud.html', subs=subs)


@crud.route('subscription/add/', methods=['POST', 'GET'])
def subs_crud_add():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        connect_and_iud(f'''INSERT INTO subscription(title) VALUES('{request.form['subs']}')''',
                        user=session['username'], password=session['password'])
        return redirect(url_for('admin.subscription'))
    return render_template('admin/crud/subs_crud/subs_crud_add.html')


@crud.route('user_schedule/<int:user_schedule_id>', methods=['POST', 'GET'])
def user_schedule_crud(user_schedule_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_schedule_list = connect_and_select(f'''
        SELECT public.user.id, user_schedule.id, schedule.id, first_name, last_name, date, duration
        FROM public.user
        JOIN user_schedule ON user_schedule.user_id = public.user.id
        JOIN schedule ON schedule.id = schedule_id
        WHERE user_schedule.id = {user_schedule_id};
    ''', user=session['username'], password=session['password'])
    if request.method == 'POST':
        if request.form['action'] == 'Удалить':
            connect_and_iud(f'''
                DELETE FROM user_schedule WHERE user_schedule.id = {user_schedule_id}
            ''', user=session['username'], password=session['password'])
            return redirect(url_for('admin.user_schedule'))
        if request.form['action'] == 'Изменить':
            connect_and_iud(f'''
                UPDATE schedule SET date = '{request.form['date']}' WHERE schedule.id = {user_schedule_list[0][2]};
                UPDATE schedule SET duration = '{request.form['duration']}' WHERE schedule.id = {user_schedule_list[0][2]};
            ''', user=session['username'], password=session['password'])
            return redirect(url_for('admin.user_schedule'))
    return render_template('admin/crud/user_schedule/user_schedule_crud.html', user_schedule_list=user_schedule_list)


@crud.route('user_schedule/add', methods=['POST', 'GET'])
def user_schedule_crud_add():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_select(f'''
        SELECT public.user.id, first_name, last_name
        FROM public.user
        WHERE status_id != 4;
    ''', user=session['username'], password=session['password'])
    if request.method == 'POST':
        user_dict = {}
        for item in user_list:
            user_dict[' '.join([item[1], item[2]])] = item[0]
        connect_and_iud(f'''
            INSERT INTO schedule(date, duration)
            VALUES('{request.form['date']}', '{request.form['dur']} hours');
        ''', user=session['username'], password=session['password'])
        last_schedule = connect_and_select('''
            SELECT id FROM schedule ORDER BY id DESC LIMIT 1
        ''', user=session['username'], password=session['password'])
        connect_and_iud(f'''
            INSERT INTO user_schedule(user_id, schedule_id)
            VALUES ({user_dict[request.form['user_id']]}, {last_schedule[0][0]})
        ''', user=session['username'], password=session['password'])
        return redirect(url_for('admin.user_schedule'))
    return render_template('admin/crud/user_schedule/user_schedule_crud_add.html', user_list=user_list)


@crud.route('user_progess/<int:user_id>', methods=['POST', 'GET'])
def user_progress_crud(user_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_select(f'''
        SELECT DISTINCT public.user.id, unit_id, first_name, last_name,
        LAST_VALUE(value) OVER(PARTITION BY unit_id)
        FROM public.user
        JOIN user_progress ON user_id = public.user.id
        WHERE public.user.id = {user_id}
    ''', user=session['username'], password=session['password'])
    w_history = connect_and_select(f'''
        SELECT first_name, last_name, unit, value
        FROM public.user
        JOIN user_progress ON user_id = public.user.id
        JOIN unit ON unit.id = unit_id
        WHERE public.user.id = {user_id} AND value BETWEEN 50 AND 150
        ORDER BY public.user.id
    ''', user=session['username'], password=session['password'])
    h_history = connect_and_select(f'''
        SELECT first_name, last_name, unit, value
        FROM public.user
        JOIN user_progress ON user_id = public.user.id
        JOIN unit ON unit.id = unit_id
        WHERE public.user.id = {user_id} AND value BETWEEN 150 AND 200
        ORDER BY public.user.id
    ''', user=session['username'], password=session['password'])
    if request.method == 'POST':
        connect_and_iud(f'''
            INSERT INTO user_progress(value, user_id, unit_id)
            VALUES({request.form['h']}, {user_id}, 5);
            INSERT INTO user_progress(value, user_id, unit_id)
            VALUES({request.form['w']}, {user_id}, 1)
        ''', user=session['username'], password=session['password'])
        return redirect(url_for('admin.user_progress'))
    return render_template('admin/crud/user_progress_crud/user_progress_crud.html', user_list=user_list,
                           height=h_history, weight=w_history)


@crud.route('/user_training_schedule_attendance/<int:user_tr_sch_att_id>', methods=['GET', 'POST'])
def user_tr_sch_att_crud(user_tr_sch_att_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_select('''
            SELECT public.user.id, first_name, last_name
            FROM public.user WHERE id != 0;
        ''', user=session['username'], password=session['password'])
    status_list = connect_and_select('''SELECT * FROM attendance_status''', user=session['username'], password=session['password'])
    user_tr_sch_att_list = connect_and_select(f'''
        SELECT user_training_schedule_attendance.id, user_id, date, duration, status_id
        FROM user_training_schedule_attendance
        JOIN training_schedule ON training_schedule.id = training_schedule_id
        JOIN attendance_status ON attendance_status.id = status_id
        WHERE user_training_schedule_attendance.id = {user_tr_sch_att_id}
    ''', user=session['username'], password=session['password'])
    if request.method == 'POST':
        if request.form['action'] == 'Удалить':
            connect_and_iud(f'''
                DELETE FROM user_training_schedule_attendance WHERE id = {user_tr_sch_att_id};
            ''', user=session['username'], password=session['password'])
            return redirect(url_for('admin.user_training_schedule_attendance'))
        if request.form['action'] == 'Изменить':
            user_dict = {}
            for item in user_list:
                user_dict[' '.join([item[1], item[2]])] = item[0]
            status_dict = {}
            for item in status_list:
                status_dict[item[1].strip()] = item[0]
            connect_and_iud(f'''
                UPDATE user_training_schedule_attendance SET user_id = {user_dict[request.form['user_id']]}
                WHERE id = {user_tr_sch_att_id};
                UPDATE training_schedule SET date = '{request.form['date']}'
                WHERE id IN (SELECT training_schedule_id FROM user_training_schedule_attendance WHERE id = {user_tr_sch_att_id});
                UPDATE training_schedule SET duration = '{request.form['duration']} hours'
                WHERE id IN (SELECT training_schedule_id FROM user_training_schedule_attendance WHERE id = {user_tr_sch_att_id});
                UPDATE user_training_schedule_attendance SET status_id = {status_dict[request.form['status_id']]}
                WHERE id = {user_tr_sch_att_id};
            ''', user=session['username'], password=session['password'])
            return redirect(url_for('admin.user_training_schedule_attendance'))
    status_dict = {}
    for item in status_list:
        status_dict[item[1]] = item[0]
    return render_template('admin/crud/user_tr_sch_att_crud/user_tr_sch_att_crud.html', user_list=user_list,
                           user_tr_sch_att_list=user_tr_sch_att_list, status_list=status_list, stat=status_dict)


@crud.route('/user_training_schedule_attendance.html', methods=['POST', 'GET'])
def user_tr_sch_att_crud_add():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_select('''
        SELECT public.user.id, first_name, last_name
        FROM public.user WHERE id != 0;
    ''', user=session['username'], password=session['password'])
    if request.method == 'POST':
        user_dict = {}
        for item in user_list:
            user_dict[' '.join([item[1], item[2]])] = item[0]
        connect_and_iud(f'''
            INSERT INTO training_schedule(date, duration)
            VALUES('{request.form['date']}', '{request.form['duration']} hours')
        ''', user=session['username'], password=session['password'])
        last_tr_sch = connect_and_select(f'''
            SELECT id
            FROM training_schedule
            ORDER BY id DESC LIMIT 1;
        ''', user=session['username'], password=session['password'])
        connect_and_iud(f'''
            INSERT INTO user_training_schedule_attendance(user_id, training_schedule_id)
            VALUES ({user_dict[request.form['user_id']]}, {last_tr_sch[0][0]});
        ''', user=session['username'], password=session['password'])
        return redirect(url_for('admin.user_training_schedule_attendance'))
    return render_template('admin/crud/user_tr_sch_att_crud/user_tr_sch_att_crud_add.html', user_list=user_list)
