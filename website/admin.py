from flask import Blueprint, render_template, redirect, session, url_for

from . import connect_and_execute_query

admin = Blueprint('admin', __name__)


@admin.route('/')
def home():
    if session['status'] == 'клиент':
        return redirect(url_for('main.home'))
    return render_template('admin/admin_base.html')
