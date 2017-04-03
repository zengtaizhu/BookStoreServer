#encoding:  utf-8
#蓝本中定义的程序路由
from flask import render_template, abort, redirect, url_for, flash, request,current_app 
from flask_login import login_required, current_user 
from . import main
from ..models import User, Role, Permission, Product, Category, Order, Major, Grade#表
from ..models import OrderState, SEX, Flasky_Per_Page#常量
from .forms import EditProfileForm, EditProfileAdminForm, ProductForm, OrderForm, OrderAdminForm
from ..decorators import admin_required
from .. import db
from _datetime import datetime
from flask_sqlalchemy import get_debug_queries
from alembic.command import current

#报告缓慢的数据库查询
@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters:%s\nDuration: %fs\nContext:%s\n' %
                (query.statement, query.parameters, query.duration, query.context))
    return response  

#添加商品
@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

#用户的资料编辑器路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    grades = [g.name for g in Grade.query.all()]
    majors = [m.name for m in Major.query.all()]
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.sex = SEX[int(form.sex.data)]
        current_user.grade = grades[int(form.grade.data)]
        current_user.major = majors[int(form.major.data)]#注意：form.*.data为字符串类型，应转为int类型
        current_user.location = form.location.data
        current_user.phone = form.phone.data
        current_user.more = form.more.data
        db.session.add(current_user)
        flash('您的资料信息已经更新！！！')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data = current_user.username
    form.sex.data = SEX.index(current_user.sex)#注意：form.*.data的内容为序号，因此寻找对应的数字数字顺序
    form.grade.data = grades.index(current_user.grade)
    form.major.data = majors.index(current_user.major)
    form.location.data = current_user.location
    form.phone.data = current_user.phone
    form.more.data = current_user.more
    return render_template('edit_profile.html', form=form)

#管理员的资料编辑路由
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    grades = [g.name for g in Grade.query.all()]
    majors = [m.name for m in Major.query.all()]
    if form.validate_on_submit():
        user.username = form.username.data
        user.sex = SEX[int(form.sex.data)]
        user.grade = grades[int(form.grade.data)]
        user.major = majors[int(form.major.data)]
        user.location = form.location.data
        user.phone = form.phone.data
        user.more = form.more.data
        user.role = Role.query.get(form.role.data)
        db.session.add(current_user)
        flash('您的资料信息已经更新！！！')
        return redirect(url_for('.user', username=user.username))
    form.username.data = user.username
    form.sex.data = SEX.index(current_user.sex)
    form.grade.data = grades.index(current_user.grade)
    form.major.data = majors.index(current_user.major)
    form.location.data = user.location
    form.phone.data = user.phone
    form.more.data = user.more
    form.role.data = user.role_id
    return render_template('edit_profile.html', form=form, user=user)
    
#二手书管理       
@main.route('/manager-product', methods=['GET', 'POST'])
@login_required
def manager_product():
    page = request.args.get('page', 1, type=int)#默认加载首页
    if current_user.is_administrator():#若是管理员，则加载所有的二手书信息#分页查询
        pagination = Product.query.order_by(Product.title.desc()).paginate(
            page, per_page=Flasky_Per_Page, error_out=False)#error_out请求超出页数时，False：空列表，True：返回404错误
    else:#否则，则加载该用户的出售的二手书的信息#分页查询
        pagination = Product.query.filter_by(seller_id=current_user.id).order_by(
            Product.title.desc()).paginate(page, per_page=Flasky_Per_Page, error_out=False)
    products = pagination.items#加载当前页面的记录（默认首页）
    return render_template('manager_product.html', products=products, pagination=pagination)

#二手书信息路由
@main.route('/book/<int:id>')
def product(id):
    product = Product.query.get_or_404(id)
    return render_template('product.html', products=[product])


#二手书信息编辑路由
@main.route('/edit-product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if current_user != product.seller and not current_user.can(Permission.BOOK_MANAGER):
        abort(403)#没有权限以及非本用户操作，则报错
    form = ProductForm()
    if form.validate_on_submit():
        product.title = form.title.data
        product.author = form.author.data
        product.press = form.press.data
        product.count = form.count.data
        product.price = form.price.data
        product.category = Category.query.get(form.category.data)
        product.describe = form.describe.data
        db.session.add(product)
        flash('商品信息已经更新！！！')
        return redirect(url_for('.product', id=product.id))
    form.title.data = product.title
    form.author.data = product.author
    form.press.data = product.press
    form.count.data = product.count
    form.price.data = product.price
    form.category.data = product.category_id
    form.describe.data = product.describe
    return render_template('edit_product.html', form=form)

#订单信息路由
@main.route('/order/<int:id>')
def order(id):
    order = Order.query.get_or_404(id)
    return render_template('order.html', orders=[order])

#订单信息编辑路由
@main.route('/edit-order/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_order(id):
    order = Order.query.get_or_404(id)
    if current_user != order.seller and not current_user.can(Permission.ORDER_MANAGER):
        abort(403)#没有权限以及非本用户操作，则报错
    form = OrderForm()
    if form.validate_on_submit():
        order.state = list(OrderState.values())[int(form.state.data)]
        db.session.add(order)
        flash('订单信息已经更新！！！')
        return redirect(url_for('.order', id=order.id))
    form.state.data = list(OrderState.values()).index(order.state)
    return render_template('edit_order.html', form=form)

#订单管理
@main.route('/manager-order', methods=['GET', 'POST'])
@login_required
def manager_order():
    page = request.args.get('page', 1, type=int)#默认加载首页，格式为：?page=1
    if current_user.is_administrator():#若是管理员，则加载所有的订单信息
        pagination = Order.query.order_by(Order.id.desc()).paginate(
            page, per_page=Flasky_Per_Page, error_out=False)
    else:#否则，则加载该用户的订单信息
        pagination = Order.query.filter_by(seller_id=current_user.id).order_by(
            Order.id.desc()).paginate(page, per_page=Flasky_Per_Page, error_out=False)
    orders = pagination.items#只加载当前页面的记录 
    return render_template('manager_order.html', orders=orders, pagination=pagination)   

