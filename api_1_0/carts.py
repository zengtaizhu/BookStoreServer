#encoding:  utf-8
#购物车
from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Cart, Permission, AnonymousUser, User, Product#表
from ..models import OrderState, Flasky_Per_Page#常量
from . import api
from .decorators import permission_required
from .errors import forbidden, unauthorized, bad_request, unfind
from flask_login import current_user
from alembic.command import current
import re
from _sqlite3 import IntegrityError

#通过买家的ID,获取订单            -------------待删除，用token代替ID
@api.route('/carts/<int:id>')
def get_carts_by_id(id):    
    u = User.query.get(id)
    if u is None:
        return forbidden('the user is not exist!')
    carts = Cart.query.filter_by(buyer=u).all()
    count = Cart.query.filter_by(buyer=u).count()
    return jsonify({'count':count,
                    'carts':[cart.to_json() for cart in carts]})

#通过令牌,获取订单
@api.route('/carts/<token>')
def get_carts(token):    
    u = User.verify_auth_token(token)
    if(u is None):
        return forbidden('token is out of time')#提示令牌超时
    carts = Cart.query.filter_by(buyer=u).all()
    count = Cart.query.filter_by(buyer=u).count()
    return jsonify({'count':count,
                    'carts':[cart.to_json() for cart in carts]})   

#添加商品到购物车   
@api.route('/carts/add/', methods=['POST'])
def add_pro_to_cart():
    d = getDict(request.get_data().decode())
    token = d['token']
    proId = d['id']
    count = int(d['count'])
    print('token=' + token + ',id=' + proId)
    u = User.verify_auth_token(token)
    if u is None:
        return unauthorized('令牌已过期!')
    p = Product.query.get(proId)
    if p is None:
        return unfind('不存在该商品，请刷新商品列表!')
#     print('变化前：商品的数量=' + str(p.totalCount))
    carts = Cart.query.filter_by(buyer=u).all()
    for cart in carts:
        list = re.findall(r'(\d+)\|(\d+),', cart.products)
        for i in list:#遍历所有的product
            if(proId == i[0]):#若找到对应的product，则将该商品数量加1
                totalCount = int(i[1]) + count
                maxCount = Product.query.get(proId).count
                if(totalCount > maxCount):
                    totalCount = maxCount
                list.remove(i)#删除旧数据
                list.append((proId, str(totalCount)))#添加新数据
#                 print('变化前：cart.products=' + cart.products + ',cart.totalprice=' + str(cart.totalprice))
                cart.totalprice += p.price#将购物车的总金额重新计算
                cart.products = ''
                for i in list:
                    cart.products += i[0] + '|' + i[1] + ','
#                     print('变化后：cart.products=' + cart.products + ',cart.totalprice=' + str(cart.totalprice))
                try:
                    db.session.commit()
#                     print('变化后：商品的数量=' + str(p.totalCount))
                    return jsonify({'result':'success', 'message':'添加到购物车成功！'})
                except IntegrityError:
                    db.session.rollback()
                    return bad_request('添加到购物车失败！') 
    cart = Cart(products=str(p.id) + '|' + str(count) + ',',
                totalprice=p.price,
                seller=p.seller,
                buyer=u)
    db.session.add(cart)
    try:
        db.session.commit()
        return jsonify({'result':'success', 'message':'添加到购物车成功！'})
    except IntegrityError:
        db.session.rollback()
        return bad_request('添加到购物车失败！')

#删除购物车
@api.route('/carts/deleteCart/', methods=['POST'])
def delete_cart():
    d = getDict(request.get_data().decode())
#     print(request.get_data().decode())
    token = d['token']
    id = d['id']
    print('token=' + token + ',id=' + id)
    u = User.verify_auth_token(token)
    if u is None:
        return unauthorized('令牌已过期!')
    cart = Cart.query.get(int(id))
    if cart is None:
        return unfind('找不到该购物车，请刷新重试!')
    db.session.delete(cart)
    try:
        db.session.commit()
        return jsonify({'result':'success',
                        'message':'删除购物车成功!'})
    except IntegrityError:
        db.session.rollback()
        return bad_request('删除购物车失败！')

#删除购物车中的商品
@api.route('/carts/delete/', methods=['POST'])
def delete_cart_pro():
    d = getDict(request.get_data().decode())
#     print(request.get_data().decode())
    token = d['token']
    id = str(d['id'])
    proId = str(d['proId'])
    u = User.verify_auth_token(token)
    if u is None:
        return unauthorized('令牌已过期!')
    cart = Cart.query.get(id)
    if cart is None:
        return unfind('找不到该购物车，请刷新重试!')
    list = re.findall(r'(\d+)\|(\d+),', cart.products) 
    count = 0
    for i in list:#遍历商品
        if(proId == i[0]):
            count = int(i[1])
            list.remove(i)#删除此数据
            break
    cart.products = ''
    for i in list:
        cart.products += i[0] + '|' + i[1] + ','
    p = Product.query.get(proId)
    cart.totalprice -= p.price * count 
    try:
        db.session.commit()
        return jsonify({'result':'success', 'message':'删除购物车商品成功！'})
    except IntegrityError:
        db.session.rollback()
        return bad_request('删除购物车商品失败！')  

#将Post请求的内容解析为字典格式，如'id=123&password=123&'-->{'id':123, 'password':'123'}
def getDict(content):
    return dict(re.findall('(.*?)=(.*?)&', content))
    
    
    