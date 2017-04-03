#encoding:  utf-8
#用户
from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from .errors import forbidden, unauthorized, bad_request, unfind
from ..models import User, Order, Product, Grade, Major#表
from ..models import OrderState, Flasky_Per_Page, PIC_PATH#常量
from sqlalchemy.exc import IntegrityError
import re 
import forgery_py#随机生成数
from datetime import datetime
import os
import urllib.parse

#通过Id，获得用户(不包括令牌和密码)
@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(int(id))
    return jsonify(user.to_json())
    
@api.route('/users/<int:id>/products/')
def get_users_own_products(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.filter_by(seller=user).paginate(
        page, per_page=Flasky_Per_Page, error_out=False)
    products = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_users_own_products', page=page+1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_users_own_products', page=page-1, _external=True)
    return jsonify({
        'products':[product.to_json() for product in products],
        'next':next,
        'prev':prev,
        'count':pagination.total
        })
 
#通过手机号，确认手机是否已注册
@api.route('/users/phone/<int:phone>')
def check_user_isExist(phone):
    u = User.query.filter_by(phone = int(phone)).first()
    if u is None:
#         print('该手机号尚未注册')
        return unfind('该手机号尚未注册!')
    return jsonify({'result':'success',
                    'message':'该手机号已注册!'})
  
#通过ID，获取用户(包括Token令牌)
@api.route('/users/phone/', methods=['POST']) 
def get_user_by_id():
    d = getDict(request.get_data().decode())
    u = User.query.get_or_404(d['id'])
#     print(u.to_json_with_token())
    return jsonify(u.to_json_with_token())

#注册新用户
@api.route('/users/register/', methods=['POST'])
def register_user():
    d = getDict(request.get_data().decode())
#     print('id=' + d['id'] + ',password=' + d['password'] + ',phone=' + phoned['id'])
    u = User(id=d['id'], password=d['password'], phone=d['id'])
    db.session.add(u)
    try:
        db.session.commit()
#         print('添加用户成功！')
        return jsonify({'result':'success'})
    except IntegrityError:
        db.session.rollback()
#         print('添加用户失败！')
        return jsonify({'result':'error'})
 
#修改密码
@api.route('/users/modifyPassword/', methods=['POST'])
def modify_password():
    d = getDict(request.get_data().decode())
    id = d['id']
    password = d['password']
#     print('id=' + id + ', password=' + password)
    u = User.query.filter_by(phone=id).first()
    if u is None:
#         print('不存在该用户')
        return unfind('不存在该用户!')
    u.password = password
    if(u.verify_password(password)):
#         print('修改用户密码成功')
        return jsonify({'result':'success',
                        'message':'修改用户密码成功!'})
    else:
#         print('修改密码失败')
        return bad_request('修改密码失败!')
 
#通过令牌，修改收货地址 
@api.route('/modify/userLocation/', methods=['POST'])
def modify_user_location():
    d = getDict(request.get_data().decode())
    token = d['token']
    location = d['location']
#     print('token=' + token + ',location=' + location)
    u = User.verify_auth_token(token)
    if u is None:
       return unauthorized('令牌已过期！')
    u.location = urllib.parse.unquote(location)
    db.session.add(u)
    db.session.commit()
    return jsonify({'result':'success',
                    'message': '修改用户收货地址成功！'})

#通过令牌，修改用户头像  
@api.route('/users/modifyUserImg/', methods=['POST'])
def modify_user_img():
    import base64
    d = getDict(request.get_data().decode())
    token = d['token']
    image = d['image']
#     print('token=' + token + ', image=' + image)
    u = User.verify_auth_token(token)
    if u is None:
        return unauthorized('令牌已过期！')
    name = forgery_py.name.first_name() + str(u.id) + '.jpg'
    f = open(getUserLocation(name), 'wb')
    imageData = base64.b64decode(urllib.parse.unquote(image))
    f.write(imageData)
    f.close()
    newPictureUrl = getUserImageUrl(name)
    u.pictureUrl = newPictureUrl
    db.session.add(u)
    db.session.commit()
    return jsonify({'result':'success',
                    'message': newPictureUrl})

#通过令牌，修改用户名
@api.route('/modify/userName/', methods=['POST'])
def modify_user_name():
    d = getDict(request.get_data().decode())
    token = d['token']
    newUsername = d['userName']
#     print('token=' + token + ',newUsername=' + newUsername)
    u = User.verify_auth_token(token)
    if u is None:
       return unauthorized('令牌已过期！')
    u.username = urllib.parse.unquote(newUsername)
    db.session.add(u)
    db.session.commit()
    return jsonify({'result':'success',
                    'message': '修改用户名成功！'})

#通过令牌，修改用户性别
@api.route('/modify/userSex/', methods=['POST'])
def modify_user_sex():
    d = getDict(request.get_data().decode())
    token = d['token']
    sex = d['sex']
#     print('token=' + token + ',sex=' + sex)
    u = User.verify_auth_token(token)
    if u is None:
       return unauthorized('令牌已过期！')
    u.sex = urllib.parse.unquote(sex)
    db.session.add(u)
    db.session.commit()
    return jsonify({'result':'success',
                    'message': '修改用户性别成功！'})

#通过令牌，修改用户专业    
@api.route('/modify/userMajor/', methods=['POST'])
def modify_user_major():
    d = getDict(request.get_data().decode())
    token = d['token']
    major = d['major']
    print('token=' + token + ',major=' + major)
    u = User.verify_auth_token(token)
    if u is None:
       return unauthorized('令牌已过期！')
    u.major = urllib.parse.unquote(major)
    db.session.add(u)
    db.session.commit()
    return jsonify({'result':'success',
                    'message': '修改用户专业成功！'})
    
#通过令牌，修改用户年级    
@api.route('/modify/userGrade/', methods=['POST'])
def modify_user_grade():
    d = getDict(request.get_data().decode())
    token = d['token']
    grade = d['grade']
    print('token=' + token + ',grade=' + grade)
    u = User.verify_auth_token(token)
    if u is None:
       return unauthorized('令牌已过期！')
    u.grade = urllib.parse.unquote(grade)
    db.session.add(u)
    db.session.commit()
    return jsonify({'result':'success',
                    'message': '修改用户年级成功！'})
 
#获得专业列表   
@api.route('/user/majors/')
def get_majors():
    majors = Major.query.all()
    l = []
    for m in majors:
        l.append(m.name)
    return jsonify({'result':'success',
                    'message':','.join(l)})

#获得专业列表   
@api.route('/user/grades/')
def get_grades():
    grades = Grade.query.all()
    l = []
    for g in grades:
        l.append(g.name)
    return jsonify({'result':'success',
                    'message':','.join(l)})

#将Post请求的内容解析为字典格式，如'id=123&password=123&'-->{'id':123, 'password':'123'}
def getDict(content):
    return dict(re.findall('(\w+)=(.*?)&', content))

#获得用户头像的URL
def getUserImageUrl(name):
    path = url_for('api.modify_user_img', _external=True)#path格式为：http://192.168.0.1:5000/api/v1.0/users/.../..
    l = path.split('/')#list为['http:', '', '192.168.191.1:5000', 'api', 'v1.0', 'users', ...]
    return '/'.join(l[0:3]) + '/static' + '/picture' + '/users/' + name;
    
#获得用户头像的本地路径   
def getUserLocation(name):
    path = PIC_PATH + '\\users'
    if(os.path.exists(path) == False):#先查看是否存在该文件夹
        os.makedirs(path)
    return path + '\\' + name



