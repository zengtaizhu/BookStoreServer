#encoding:  utf-8
#创建蓝本
from flask import Blueprint

main = Blueprint('main', __name__)

#把路由和错误处理程序与蓝本关联起来
from . import views, errors
from ..models import Permission

#使用上下文处理器，使得变量可以在所有模板中（蓝本内外）全局访问
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)