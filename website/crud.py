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


@crud.route('/users/add', methods=['POST', 'GET'])
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


@crud.route('/user_post/add', methods=['POST', 'GET'])
def user_post_crud_add():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    user_list = connect_and_select('''
        SELECT public.user.id, first_name, last_name
        FROM public.user
        WHERE status_id = 4;
    ''', user=session['email'].split('@')[0], password=session['password'])
    status_list = connect_and_select('''
        SELECT id, title
        FROM status
        WHERE id != 4;
    ''', user=session['email'].split('@')[0], password=session['password'])
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
        ''', user=session['email'].split('@')[0], password=session['password'])
        return redirect(url_for('admin.user_post'))
    return render_template('admin/crud/user_post_crud/user_post_crud_add.html', user_list=user_list,
                           status_list=status_list)


@crud.route('subscription_duraion/<int:subs_dur_id>', methods=['POST', 'GET'])
def subs_dur_crud(subs_dur_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    subs_dur = connect_and_select(f'''SELECT * FROM subscription_duration WHERE id = {subs_dur_id};''',
                                  user=session['email'].split('@')[0], password=session['password'])
    if request.method == 'POST':
        if request.form['action'] == 'Удалить':
            connect_and_iud(f'''DELETE FROM subscription_duration WHERE id = {subs_dur_id}''',
                            user=session['email'].split('@')[0], password=session['password'])
            return redirect(url_for('admin.subscription_duration'))
        if request.form['action'] == 'Изменить':
            connect_and_iud(f'''
                UPDATE subscription_duration SET duration = '{request.form['subs_dur']}' WHERE id = {subs_dur_id};
            ''', user=session['email'].split('@')[0], password=session['password'])
            return redirect(url_for('admin.subscription_duration'))
    return render_template('admin/crud/subs_dur_crud/subs_dur_crud.html', subs_dur=subs_dur)


@crud.route('subscription_duraion/add', methods=['POST', 'GET'])
def subs_dur_crud_add():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        connect_and_iud(f'''
            INSERT INTO subscription_duration(duration) VALUES('{request.form['subs_dur']} day');
        ''', user=session['email'].split('@')[0], password=session['password'])
        return redirect(url_for('admin.subscription_duration'))
    return render_template('admin/crud/subs_dur_crud/subs_dur_crud_add.html')


@crud.route('subscription/<int:subs_id>', methods=['POST', 'GET'])
def subs_crud(subs_id):
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    subs = connect_and_select(f'''SELECT * FROM subscription WHERE id = {subs_id};''',
                              user=session['email'].split('@')[0], password=session['password'])
    if request.method == 'POST':
        if request.form['action'] == 'Удалить':
            connect_and_iud(f'''DELETE FROM subscription WHERE id = {subs_id}''', user=session['email'].split('@')[0],
                            password=session['password'])
            return redirect(url_for('admin.subscription'))
        if request.form['action'] == 'Изменить':
            connect_and_iud(f'''UPDATE subscription SET title = '{request.form['subs']}' WHERE id = {subs_id}''',
                            user=session['email'].split('@')[0], password=session['password'])
            return redirect(url_for('admin.subscription'))
    return render_template('admin/crud/subs_crud/subs_crud.html', subs=subs)


@crud.route('subscription/add/', methods=['POST', 'GET'])
def subs_crud_add():
    if session['status'] not in ['Тренер', 'Администратор', 'Управляющий']:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        connect_and_iud(f'''INSERT INTO subscription(title) VALUES('{request.form['subs']}')''',
                        user=session['email'].split('@')[0], password=session['password'])
        return redirect(url_for('admin.subscription'))
    return render_template('admin/crud/subs_crud/subs_crud_add.html')
