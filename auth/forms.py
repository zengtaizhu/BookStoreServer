#encoding:  utf-8
#登录表单
from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Required, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

#登录表单
class LoginForm(Form):
    account = StringField('账户', validators=[Required()])
    password = StringField('密码', validators=[Required()])
    remember_me = BooleanField('记住我的账号')
    submit = SubmitField('登录')


#注册表单
class RegistrationForm(Form):
    id = StringField('学号', validators=[Required(), Regexp('\d{12}', 0, '请正确输入学号！！！')])
    username = StringField('姓名', validators=[Required(), Length(1, 64)])
    password = PasswordField('密码', validators=[
        Required(), EqualTo('password2', message='密码和确认密码必须一致！！！')])
    password2 = PasswordField('确认密码', validators=[Required()])
    grade = StringField('年级', validators=[Length(0, 64), Required()])
    major = StringField('专业', validators=[Length(0, 64), Required()])
    location = StringField('宿舍号', validators=[Length(1, 64), Required()])
    phone = StringField('电话', validators=[Required(), Regexp('\d{11}', 0, '请正确输入电话号码！！！')])
    submit = SubmitField('注册')
    
    def validate_id(self, field):
        if User.query.filter_by(id=field.data).first():
            raise ValidationError('该学号已有人注册了！！！')

#修改密码表单
class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='确认密码必须与新密码一致！！！')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('确认修改')
    

    
    

        