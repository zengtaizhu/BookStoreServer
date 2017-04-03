#encoding:  utf-8
#创建蓝本
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
