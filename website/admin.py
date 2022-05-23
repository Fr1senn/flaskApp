from flask import Blueprint, render_template, redirect, session, url_for

from . import connect_and_execute_query

admin = Blueprint('admin', __name__)


@admin.route('/')
def home():
    if session['status'] == 'клиент':
        return redirect(url_for('main.home'))
    return render_template('admin/admin_base.html')


@admin.route('/users')
def users():
    if session['status'] == 'клиент':
        return redirect(url_for('main.home'))
    user_list = connect_and_execute_query('''SELECT * FROM public.user''',
                                          user=session['email'].split('@')[0],
                                          password=session['password'])
    return render_template('admin/users.html', users=user_list)


@admin.route('/reviews')
def reviews():
    if session['status'] == 'клиент':
        return redirect(url_for('main.home'))
    review_list = connect_and_execute_query('''
    SELECT first_name, last_name, email, text, date
    FROM public.user
    JOIN review ON user_id = public.user.id;''', user=session['email'].split('@')[0], password=session['password'])
    return render_template('admin/reviews.html', reviews=review_list)


@admin.route('/user_progress')
def user_progress():
    if session['status'] == 'клиент':
        return redirect(url_for('main.home'))
    user_progress_list = connect_and_execute_query('''
        SELECT first_name, last_name, email, date, value, unit
        FROM public.user
        JOIN user_progress ON user_id = public.user.id
        JOIN unit ON unit.id = unit_id''', user=session['email'].split('@')[0], password=session['password'])
    return render_template('admin/user_progress.html', user_progress=user_progress_list)


@admin.route('/user_schedule')
def user_schedule():
    if session['status'] == 'клиент':
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
    if session['status'] == 'клиент':
        return redirect(url_for('main.home'))
    user_post_list = connect_and_execute_query('''
        SELECT first_name, last_name, title, salary, date
        FROM public.user
        JOIN user_post ON user_id = public.user.id
        JOIN post ON post.id = post_id''', user=session['email'].split('@')[0], password=session['password'])
    return render_template('admin/user_schedule.html', user_post=user_post_list)


@admin.route('/user_subs_dur')
def user_subs_dur():
    if session['status'] == 'клиент':
        return redirect(url_for('main.home'))
    user_subs_dur_list = connect_and_execute_query('''
        SELECT first_name, last_name, title, duration, date, price
        FROM public.user
        JOIN user_subscription_duration ON user_id = public.user.id
        JOIN subscription ON subscription.id = subscription_id
        JOIN subscription_duration ON subscription_duration.id = subscription_duration_id''',
                                                   user=session['email'].split('@')[0], password=session['password'])
    return render_template('admin/user_subs_dur.html', user_subs_dur=user_subs_dur_list)


@admin.route('/user_tr_sch_att')
def user_tr_sch_att():
    if session['status'] == 'клиент':
        return redirect(url_for('main.home'))
    user_tr_sch_att_list = connect_and_execute_query('''
        SELECT first_name, last_name, attendance, title
        FROM public.user
        JOIN user_training_schedule_attendance ON user_id = public.user.id
        JOIN attendance ON attendance.id = attendance_id
        JOIN training_schedule_equipment ON training_schedule_equipment.id = training_schedule_equipment_id
        JOIN equipment ON equipment.id = equipment_id''', user=session['email'].split('@')[0],
                                                     password=session['password'])
    return render_template('admin/user_tr_sch_att.html', user_tr_sch_att=user_tr_sch_att_list)
