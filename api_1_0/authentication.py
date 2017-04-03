#encoding:  utf-8
#Flask-http认证协议
from flask import g, jsonify, request
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import forbidden, unauthorized
import json
import re

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(id_or_token, password):
    if id_or_token == '':#如果账号或令牌为空，则默认使用匿名用户
        g.current_user = AnonymousUser()
        return True
    if password == '':#如果密码为空，则查看令牌是否有效
        g.current_user = User.verify_auth_token(id_or_token)
        g.token_used = True#区分验证两种方式，True：令牌，False：账号密码
        return g.current_user is not None
    user = User.query.get(id)
    if not user:#检验该用户是否存在
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)#验证密码

@auth.error_handler#错误处理程序
def auth_error():
    return unauthorized('Invalid credentials')#返回未授权访问错误

@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and g.current_user.password is None:
        return forbidden('No login')


#测试：http --auth : --json POST http://127.0.0.1:5000/api/v1.0/token/ id=201330350225 password=123
#通过传入账号和密码，获取用户信息(用令牌代替密码)
@api.route('/token/', methods=['POST'])
def get_token():
    d = getDict(request.get_data().decode())
    id = d['id']
    password = d['password']
#     print('id=' + id + ',password=' + password)
    u = User.query.get(id)
#     print('username = ' + u.username)
    if u is None:
        return forbidden('该账号')
    if u.verify_password(password):
#         print('密码正确')
        return jsonify({'result':'success',
                        'message':str(u.to_json_with_token())})
    else:
#         print('密码错误')
        return forbidden('password error密码错误')
    
#测试：http --auth : --json POST http://127.0.0.1:5000/api/v1.0/verify/ token=123
#通过发送token令牌，获得用户信息(用令牌代替密码)
@api.route('/verify/', methods=['POST'])
def verify_token():
    content = request.data.decode()
    d = eval(content)
    token = d['token']
    u = User.verify_auth_token(token)
    if u is not None:
        return jsonify({'user':u.to_json_with_token()})
    else:
        return forbidden('token is error')


#将Post请求的内容解析为字典格式，如'id=123&password=123&'-->{'id':123, 'password':'123'}
def getDict(content):
    return dict(re.findall('(\w+)=(.*?)&', content))
