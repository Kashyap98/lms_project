from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from models.User import User, RegistrationForm, LoginForm
from flask_app import db

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    form = LoginForm()
    return render_template('user/login.html', form=form, title="Log in")


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    form = RegistrationForm()
    return render_template('user/signup.html', title='Register', form=form)


@auth.route('/signup', methods=['POST'])
def signup_post():
    form = RegistrationForm()

    if form.validate_on_submit():
        # convert password to hashed
        form.password.data = generate_password_hash(form.password.data)
        flash(f'Account created for {form.name.data}!', 'success')
        user = User()
        form.populate_obj(user)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    else:
        if "email" in form.errors:
            flash('Email must be unique.')
        return render_template('user/signup.html', title='Register', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
