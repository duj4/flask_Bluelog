from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from bluelog.models import Admin
from bluelog.forms import LoginForm
from bluelog.utils import redirect_back

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 已经登录的用户不小心访问了这个视图，通过if将已经登录的用户重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()

        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash('Welcome back.', 'info')
                return redirect_back()
            flash('Invalid username or password.', 'warning')
        else:
            flash('No account.', 'warning')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
# 视图保护装饰器，需要登录才能访问的视图前加上这个装饰器
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()