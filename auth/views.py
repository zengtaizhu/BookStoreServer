#encoding:  utf-8
#登录蓝本中定义的程序路由
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePasswordForm
from .. import db

#每次auth蓝本启动前，更新已登录用户的访问时间
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
#         if request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
#             return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

#登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.account.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            #查询字符串next保存原始地址
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('账号或密码错误！！！')
    return render_template('auth/login.html', form=form)

#注册
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(id=form.id.data,
                    username=form.username.data,
                    password=form.password.data,
                    grade=form.grade.data,
                    major=form.major.data,
                    location=form.location.data,
                    phone=form.phone.data)
        db.session.add(user)
        db.session.commit()
        flash('您现在可以登录了！！！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

#修改密码
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('您的密码已经修改完成！！！')
            return redirect(url_for('main.index'))
        else:
            flash('请输入正确的原密码！！！')
    return render_template('auth/change_password.html', form=form)

#退出登录
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经退出登录！！！')
    return redirect(url_for('main.index'))