#encoding:  utf-8
#API蓝本的构造文件
from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, errors, orders, products, categories, users, carts


