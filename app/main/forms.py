from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required,Email,URL,EqualTo,Length,Regexp
from wtforms import StringField,SubmitField,PasswordField,validators,SelectField
from ..models import SVSuserReg


#This form function will render user profile edit page.
class EditProfileForm(Form):
    Firstname = StringField('First name', validators=[Length(0, 64)])
    LastName = StringField('Last name', validators=[Length(0, 64)])
    mobile = StringField('Mobile No', validators=[Length(0, 64)])
    submit = SubmitField('Submit')

def validate_email(self, field):
        if field.data != self.user.email and   SVSuserReg.query.filter_by(emid=field.data).first():
            raise ValidationError('Email already registered.')

def validate_username(self, field):
        if field.data != self.user.username and  SVSuserReg.query.filter_by(fname=field.data).first():
            raise ValidationError('Username already in use.')