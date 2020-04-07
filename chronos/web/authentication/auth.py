from flask import Blueprint, render_template, request, url_for, flash, Markup
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from chronos.model import User
from chronos import db, log
from chronos.web.forms import LoginForm, SignupForm


auth = Blueprint('auth', __name__)
# auth.template_folder = 'templates'
# log.info(auth.template_folder)


@auth.route('/login', methods=('GET', 'POST'))
def login():
    log.info(auth.template_folder)
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))  # if user doesn't exist or password is wrong, reload the page
        login_user(user, remember=remember)
        return redirect(url_for('user.profile'))
    return render_template('login.html', form=form)


@auth.route('/signup', methods=('GET', 'POST'))
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()  # check if email address exists in database
        if user:  # leave a message if the email address exists
            flash(Markup('Email address already exists. Go to the <a href="login">login page</a>.'))
            return redirect(url_for('auth.signup'))
        # noinspection PyArgumentList
        new_user = User(email=email,
                        username=username,
                        password=generate_password_hash(password, method='sha256'),
                        is_anonymous=False)
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('user.profile'))
    return render_template('signup.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user.index'))