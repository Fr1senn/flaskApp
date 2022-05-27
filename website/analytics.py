from flask import Blueprint, render_template, request, redirect, session, url_for, flash

from website import connect_and_select, connect_and_iud

analytics = Blueprint('analytics', __name__)


@analytics.route('/income')
def income():
    if session['status'] not in ['Управляющий']:
        return redirect(url_for('main.home'))
    inc = connect_and_select(f'''
        WITH month_list AS(
            SELECT ml FROM generate_series(1, 12) AS ml
        ),
        d AS(
            SELECT DISTINCT ml,
            SUM(COALESCE(price, 0)) OVER(PARTITION BY ml) AS monthly_income
            FROM month_list
            LEFT JOIN user_subscription_duration ON ml = EXTRACT(MONTH FROM date)
            ORDER BY ml
        )
        SELECT * FROM d;
    ''', user=session['username'], password=session['password'])
    return render_template('admin/analytics/income.html', income=inc)


@analytics.route('/subscription_rank')
def subs_rank():
    if session['status'] not in ['Управляющий']:
        return redirect(url_for('main.home'))
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
        GROUP BY title;
    ''', user=session['username'], password=session['password'])
    return render_template('admin/analytics/subs_rank.html', rank=rank)