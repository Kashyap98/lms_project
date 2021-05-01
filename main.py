from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import text

main = Blueprint('main', __name__)
from flask_app import db


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    # get name from database
    sql = text(f'select name from user WHERE id = {current_user.id}')
    result = db.engine.execute(sql)

    # get name for user from result
    name = [row[0] for row in result][0]
    return render_template('user/profile.html', name=name, title=f"Profile | {name}")
