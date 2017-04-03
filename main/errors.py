#encoding:  utf-8
#蓝本的错误处理程序
from flask import render_template, request, jsonify
from . import main

#使用app_errorhandler来注册程序全局的错误处理程序
@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@main.app_errorhandler(404)#使用HTTP内容协商处理错误，根据请求的内容回应相对的格式
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error':'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
