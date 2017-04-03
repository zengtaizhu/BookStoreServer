#encoding:  utf-8
#检查用户权限的自定义修饰器
from functools import wraps
from flask import g
from .errors import forbidden

def permission_required(permission):#检查当前用户是够有permission权限
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')#权限不足
            return f(*args, **kwargs)
        return decorated_function
    return decorator
        
        
        