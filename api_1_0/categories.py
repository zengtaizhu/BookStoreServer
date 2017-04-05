#encoding:  utf-8
#商品类
from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from . import api
from .decorators import permission_required
from .errors import forbidden
from ..models import Product, Permission, Category, Grade#表

#获取商品类         -------------待修改，将没有Product的数据剔除
@api.route('/categories/')
def get_categories():
    categories = []
    for c in Category.query.all():
        if(Product.query.filter_by(category=c).count() > 0):
            categories.append(c)
    count = len(categories)
    return jsonify({'count':count,
                    'categories':[category.to_json() for category in categories]
                    })

#获得适合年级列表
@api.route('/categories/grade/')
def get_grade_gategory():
    grades = [grade.name for grade in Grade.query.all()]
#     print(','.join(grades))
    return jsonify({'result':'success',
                    'message':','.join(grades)})