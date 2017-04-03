#encoding:  utf-8
#主蓝本的Form
from flask_wtf import Form
from wtforms import StringField, SubmitField, RadioField, TextAreaField, SelectMultipleField
from wtforms import SubmitField, SelectField, BooleanField, IntegerField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Regexp, NumberRange
from ..models import Role, User, Category, Order, Product, Grade, Major#表
from ..models import OrderState, SEX#常量
from random import choice
from email.policy import default


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')
    
   
#普通用户的资料编辑器
class EditProfileForm(Form):
    username = StringField('姓名', validators=[Length(1, 64)])
    sex = RadioField('性别', coerce=int)
    grade = SelectField('年级', coerce=int)
    major = SelectField('专业', coerce=int)
    location = StringField('宿舍号', validators=[Length(1, 64)])
    phone = StringField('电话', validators=[Required(), Regexp('\d{11}', 0, '请正确输入电话号码！！！')])
    more = TextAreaField('附加信息')
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        grades = [g.name for g in Grade.query.all()]
        majors = [m.name for m in Major.query.all()]
        self.sex.choices = [(x, SEX[x])
                            for x in range(len(SEX))]
        self.grade.choices = [(x, grades[x])
                              for x in range(len(grades))] 
        self.major.choices = [(x, majors[x])
                              for x in range(len(majors))]
        
    
  
#管理员的资料编辑器
class EditProfileAdminForm(Form):
    username = StringField('姓名', validators=[Length(1, 64), Required()])
    grade = SelectField('年级', coerce=int)
    sex = RadioField('性别', coerce=int)
    major = SelectField('专业', coerce=int)
    role = SelectField('角色', coerce=int)#coerce：将字段的值转化为整数
#     confirmed = BooleanField('已确认？')
    location = StringField('住址', validators=[Length(1, 64), Required()])
    phone = StringField('电话', validators=[
        Required(), Regexp('\d{11}', 0, '请正确输入电话号码！！！')])
    more = TextAreaField('附加信息')
    submit = SubmitField('提交')
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        grades = [g.name for g in Grade.query.all()]
        majors = [m.name for m in Major.query.all()]
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.sex.choices = [(x, SEX[x])
                            for x in range(len(SEX))]
        self.grade.choices = [(x, grades[x])
                              for x in range(len(grades))] 
        self.major.choices = [(x, majors[x])
                              for x in range(len(majors))]
        self.user = user
    
    #验证电话的正确性，保证一个电话号码只能被一个用户注册
#     def validate_phone(self, field):
#         if field.data != self.user.phone and User.query.filter_by(phone=field.data).first():
#             raise ValidationError('该电话号码已被注册！！！')


#商品信息的编辑器
class ProductForm(Form):
    title = StringField('书名', validators=[Required()])
    author = StringField('作者', validators=[Required()])
    press = StringField('出版社', validators=[Required()])
    count = IntegerField('数量', validators=[Required(), NumberRange(0, 10000)])
    price = StringField('价格', validators=[
        Required(), Regexp('\d{1,10}(\.\d{1,2})?', 0, '请正确输入图书价格')])
    category = SelectField('商品类别', coerce=int)#coerce：将字段的值转化为整数
    describe = TextAreaField('详细描述')
    submit = SubmitField('提交')
        
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


#用户的订单信息编辑器
class OrderForm(Form):
    state = SelectField('订单状态', coerce=int)
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.state.choices = [(x, list(OrderState.values())[x])
                              for x in range(len(OrderState))]
        

#管理员的订单信息编辑器        #-------------待删除
class OrderAdminForm(Form):
    products = SelectMultipleField('商品', coerce=int)
    state = SelectField('订单状态', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(OrderAdminForm, self).__init__(*args, **kwargs)
        self.state.choices = [(x, list(s.values())[x])
                              for x in range(len(OrderState))]
        self.products.choices = [(product.id, product.id)
                                 for product in Product.query.order_by(Product.id).all()]
