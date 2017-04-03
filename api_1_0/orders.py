 #encoding:  utf-8
#订单
from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Order, Permission, AnonymousUser, User, Product#表
from ..models import OrderState, Flasky_Per_Page#常量
from . import api
from .decorators import permission_required
from .errors import forbidden, unfind, bad_request, unauthorized
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from alembic.command import current
import re
import urllib.parse

#获取订单，分页获取订单                                                  #测试成功-----------待删除
@api.route('/orders/')
def get_orders():
    page = request.args.get('page', 1, type=int)
    pagination = Order.query.paginate(
        page, per_page=Flasky_Per_Page, error_out=False)
    orders = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_orders', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_orders', page=page+1, _external=True)
    return jsonify({'orders': [order.to_json() for order in orders],
                    'count': pagination.total,
                    'prev': prev,
                    'next': next
                    })

#获取订单，通过Order.buyer_id才能获取订单                    
@api.route('/orders/<int:id>')
# @permission_required(Permission.ORDER_MANAGER)
def get_order(id):
    order = Order.query.get_or_404(id)
    return jsonify(order.to_json())

#通过用户ID，获取订单            ---------------待删除 应使用下面的令牌Token
@api.route('/orders/user/<int:id>')
def get_order_by_user(id):
    orders = Order.query.filter_by(buyer_id=id).all()
    count = len(orders)
    return jsonify({'orders': [order.to_json() for order in orders],
                    'count': count
                    })

#通过令牌Token，获取订单
@api.route('/orders/user/<token>')
def get_order_by_token(token):
    u = User.verify_auth_token(str(token))
    if(u is None):
        return forbidden('token is out of time')#提示令牌超时
    orders = Order.query.filter_by(buyer=u).all()
    count = len(orders)
    return jsonify({'count': count,
                    'orders': [order.to_json() for order in orders]
                    })

#通过令牌和订单的状态加载订单
@api.route('/orders/user/', methods=['POST'])
def get_order_by_state():
    d = getDict(request.get_data().decode())
    state = d['state']
    token = d['token']
#     print('token=' + token + ',state=' + state)
    u = User.verify_auth_token(token)
    if u is None:
        return forbidden('token is out of time')#提示令牌超时
    orders = Order.query.filter_by(buyer=u).filter_by(state=OrderState[state]).all()
    count = len(orders)
    return jsonify({'count':count,
                    'orders':[order.to_json() for order in orders]
                    })

#创建订单，只有登录后才可以创建订单
@api.route('/orders/add/', methods=['POST'])
def new_order():
    d = getDict(request.get_data().decode())
    token = d['token']
    products = urllib.parse.unquote(d['products'])
    totalPrice = d['totalprice']
    comment = urllib.parse.unquote(d['comment'])
    sellerId = d['seller']
    orderId = d['orderId']
    sendWay = urllib.parse.unquote(d['sendWay'])
#     print('token=' + token + ',products=' + products + ',price=' + totalPrice + ',sendWay=' 
#           + sendWay + ',comment=' + comment + ',seller=' + sellerId + ',orderId=' + orderId)
    buyer = User.verify_auth_token(token)
    if buyer is None:
        return unauthorized('令牌已过期！')
    seller = User.query.get(int(sellerId))
    if seller is None:
        return unfind('找不到卖家!')
    order = Order(products=products,
                  orderId=orderId,
                  phone=buyer.phone,
                  address=buyer.location,
                  totalprice=float(totalPrice),
                  comment=comment,
                  sendWay=sendWay,
                  seller=seller,
                  buyer=buyer)
    db.session.add(order)
    try:
        db.session.commit()
        list = re.findall(r'(\d+)\|(\d+),', products) 
        for item in list:
            p = Product.query.get(int(item[0]))#遍历商品
            p.count = p.count - int(item[1])#减少商品的库存数量
            db.session.add(p)
            try:
                db.session.commit()
                return bad_request('支付失败!')
            except IntegrityError:
                db.session.rollback()
                pass
    except IntegrityError:
        db.session.rollback()
        return bad_request('支付失败!')
    return jsonify({'result':'success',
                        'message':'支付成功!'})
    
#编辑订单，即修改订单的状态
@api.route('/orders/modify/', methods=['POST'])
def edit_order():
    d = getDict(request.get_data().decode())
    token = d['token']
    id = d['id']
    state = d['state']
    print('token=' + token + ',Orderid=' + id + ',state=' + state)
    u = User.verify_auth_token(token)
    if u is None:
        return unauthorized('令牌已过期!')
    order = Order.query.get(int(id))
    order.state = OrderState.get(state)
    db.session.add(order)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return bad_request('修改订单状态失败!')
    return jsonify({'result':'success',
                        'message':'修改订单状态成功!'})
    
#编辑订单，评价订单
@api.route('/orders/comment/', methods=['POST'])
def comment_order():
    d = getDict(request.get_data().decode())
    token = d['token']
    id = d['id']
    comment = urllib.parse.quote(d['comment'])
    print('token=' + token + ',Orderid=' + id + ',comment=' + comment)
    u = User.verify_auth_token(token)
    if u is None:
        return unauthorized('令牌已过期!')
    order = Order.query.get(int(id))
    order.comment = comment
    order.state = OrderState.get('DONE')#将订单的状态改为交易完成
    db.session.add(order)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return bad_request('评价订单失败!')
    return jsonify({'result':'success',
                        'message':'评价订单成功!'})

#将Post请求的内容解析为字典格式，如'id=123&password=123&'-->{'id':123, 'password':'123'}
def getDict(content):
    return dict(re.findall('(.*?)=(.*?)&', content))
    