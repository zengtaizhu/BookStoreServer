#encoding:  utf-8
#API错误处理
from flask import jsonify
from app.exceptions import ValidationError
from . import api

def bad_request(message):#请求错误
    response = jsonify({'message': message, 'result': 'error'})
    return response

def unauthorized(message):#未登录错误
    response = jsonify({'message': message, 'result': 'error'})
    return response

def forbidden(message):#禁止访问错误
    response = jsonify({'message': message, 'result': 'error'})
    return response

def unfind(message):#文件找不到错误
    response = jsonify({'message': message, 'result': 'error'})
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
    
