#encoding:  utf-8
#商品
from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from . import api
from .decorators import permission_required
from .errors import forbidden, unauthorized, bad_request, unfind
from ..models import Product, Permission, Comment, User, Category#表
from ..models import Flasky_Per_Page, PIC_PATH#常量
from _sqlite3 import IntegrityError
import forgery_py#随机生成数
import re
import urllib.parse
import os

#获得商品，分页获取商品 ---------待删除
@api.route('/products/')
def get_products():
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.paginate(
        page, per_page=Flasky_Per_Page, error_out=False)
    products = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_products', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_products', page=page+1, _external=True)
    return jsonify({'count': pagination.total,
                    'products': [product.to_json() for product in products],
                    'prev': prev,
                    'next': next
                    })

#根据卖家ID，获取商品列表
@api.route('/products/seller/<int:id>')
def get_products_by_seller(id):
    products = Product.query.filter_by(seller_id=int(id)).all()
    count = len(products)
    return jsonify({'count': count,
                    'products': [product.to_json() for product in products]
                    })
 
#通过商品ID，获取商品 
@api.route('/products/<int:id>')
def get_product_by_id(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.to_json())

#通过商品类型ID，分页获取商品
@api.route('/products/category/<int:id>')
def get_product_by_category(id):
    products = Product.query.filter_by(category_id=id).all()
    count = len(products)
    return jsonify({'count': count,
                    'products': [product.to_json() for product in products]
                    })

#通过关键字，获得商品    
@api.route('/products/keyword/<word>')  
def get_product_by_word(word):
    str = '%' + word + '%'
    products = Product.query.filter(Product.title.like(str)).\
        union(Product.query.filter(Product.author.like(str))).all()
    count = len(products)
    return jsonify({'count':count,
                    'products':[product.to_json() for product in products]
                    })


#获得商品推荐               ------------待修改为将搜索最多的商品推荐出来
@api.route('/products/recommend/')
def get_recommend():
    products = Product.query.filter_by(count=1).all()
    #只选取三个
    products = products[-3:len(products)]
    count = len(products)
    return jsonify({'count':count,
                    'products':[product.to_json() for product in products]
                    })
    
#通过商品ID，获取商品的评价
@api.route('/products/comment/<int:id>')
def get_comment(id):
    p = Product.query.get_or_404(id)
    comments = Comment.query.filter_by(product=p).all()
    count = Comment.query.filter_by(product=p).count()
    return jsonify({'count':count,
                    'comments':[comment.to_json() for comment in comments]
                    })

#通过令牌，删除商品  
@api.route('/products/delete/', methods=['POST'])
def delete_product():
    d = getDict(request.get_data().decode())
    token = d['token']
    id = d['id']
    print('token=' + token + ',id=' + id)
    u = User.verify_auth_token(token)
    if u is None:
        return unauthorized('令牌已过期!')
    p = Product.query.get(int(id))
    db.session.delete(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return bad_request('删除商品失败!')
    return jsonify({'result':'success',
                    'message':'删除商品成功!'})

#修改商品信息   
@api.route('/products/modify/', methods=['POST'])
def modify_product():
    import base64
    d = getDict(request.get_data().decode())
    token = d['token']
    id = int(d['id'])
    title = urllib.parse.unquote(d['title']).replace('+', ' ')
    author = urllib.parse.unquote(d['author']).replace('+', ' ')
    press = urllib.parse.unquote(d['press']).replace('+', ' ')
    count = int(d['count'])
    price = float(d['price'])
    describe = urllib.parse.unquote(d['describe']).replace('+', ' ')
#     print('proId=' + str(id) +',title=' + title + ',author=' + author + ',press=' + press + ',count' 
#           + str(count) + ',price=' + str(price) + ',describe=' + describe)
    u = User.verify_auth_token(token)
    if u is None:
        return unauthorized('令牌已过期！')
    p = Product.query.get(id)
    p.title = title
    p.author = author
    p.press = press
    p.count = count
    p.price = price
    p.describe = describe
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return bad_request('修改商品信息失败,请重试!')
    return jsonify({'result':'success',
                    'message':'修改商品信息成功!'})

#修改商品图片  
@api.route('/products/modifyImg/', methods=['POST'])
def modify_product_img():
    import base64
    d = getDict(request.get_data().decode())
    token = d['token']
    image = base64.b64decode(urllib.parse.unquote(d['image']))
    id = int(d['id'])
#     print('proId=' + str(id))
    u = User.verify_auth_token(token)
    if u is None:
        return unauthorized('令牌已过期！')
    p = Product.query.get(id)
    name = forgery_py.name.first_name() + str(id) + '.jpg'
    f = open(getProImgLocation(name), 'wb')#将图片写入本地磁盘
    f.write(image)
    f.close()
    newPirctureUrl = getPictureUrl(name)
    p.pictureUrl = newPirctureUrl
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return bad_request('修改商品图片失败,请重试!')
    return jsonify({'result':'success',
                    'message':'修改商品图片成功!'})
    
#添加商品
@api.route('/products/add/', methods=['POST'])
def add_product():
    import base64
    d = getDict(request.get_data().decode())
    token = d['token']
    image = base64.b64decode(urllib.parse.unquote(d['image']))
    title = urllib.parse.unquote(d['title']).replace('+', ' ')
    author = urllib.parse.unquote(d['author']).replace('+', ' ')
    press = urllib.parse.unquote(d['press']).replace('+', ' ')
    count = int(d['count'])
    price = float(d['price'])
    categoryId = d['categoryId']
    describe = urllib.parse.unquote(d['describe']).replace('+', ' ')
#     print('proId=' + str(id))
    u = User.verify_auth_token(token)
    if u is None:
        return unauthorized('令牌已过期！')
    name = forgery_py.name.first_name() + str(categoryId) + '.jpg'
    newPicture = getProImgLocation(name)
    f = open(newPicture, 'wb')#将图片写入本地磁盘
    f.write(image)
    f.close()
    category = Category.query.get(int(categoryId))
    p = Product(pictureUrl=getPictureUrl(name),
                title=title,
                author=author,
                press=press,
                count=count,
                price=price,
                describe=describe,
                seller=u,
                category=category)
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return bad_request('添加商品失败!')
    return jsonify({'result':'success',
                    'message':'添加商品成功!'})

#获得商品图片的本地路径   
def getProImgLocation(name):
    path = PIC_PATH + '\\products'
    if(os.path.exists(path) == False):#先查看是否存在该文件夹
        os.makedirs(path)
    return path + '\\' + name

#获得商品图片的URL
def getPictureUrl(name):
    path = url_for('api.modify_user_img', _external=True)#path格式为：http://192.168.0.1:5000/api/v1.0/users/.../..
    l = path.split('/')#list为['http:', '', '192.168.191.1:5000', 'api', 'v1.0', 'users', ...]
    return '/'.join(l[0:3]) + '/static' + '/picture' + '/products/' + name;
        
#将Post请求的内容解析为字典格式，如'id=123&password=123&'-->{'id':123, 'password':'123'}
def getDict(content):
    return dict(re.findall('(.*?)=(.*?)&', content))
    
    
    
