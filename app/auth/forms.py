
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required,Email,URL,EqualTo,Length
from wtforms import StringField,SubmitField,PasswordField,validators,SelectField, ValidationError,BooleanField
from ..models import SVSuserReg

class LoginForm(Form):
    email = StringField('Email ID:-',validators=[Required(), Length(1, 64),Email()])
    lpwd = PasswordField('Password:-', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

#This user registeration form WTF
class UserRegForm(Form):

    fname = StringField('Your FirstName:-',validators = [Required(),Length(min=1,max=56)])
    lname = StringField('Your LastName:-',validators = [Required(),Length(min=1,max=56)])
    em = StringField('Your Email ID:-',validators =[Required(),Email(),Length(min=1,max=56)])
    pwd = PasswordField('Enter Your Password:-',validators =[Required(),EqualTo('cpwd',message='Password must match')])
    cpwd = PasswordField('ReEnter Your Password:-',validators=[Required()])
    mob = StringField('Enter your mobile#:-',validators =[Required(),Length(min=10,max=10,message='Mobile no is more than 10')])
    Regsubmit = SubmitField('Register')

def validate_email(self, field):
    if SVSuserReg.query.filter_by(emid=field.data).first():
        raise ValidationError('Camera URL is already register with us')

#This is form which will update user password.
class ChangePwdform(Form):
    old_pwd = PasswordField('Old Password:-',validators=[Required()])
    password = PasswordField('New Password:-',validators=[Required(),EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Repeat Password:-',validators=[Required()])
    submit = SubmitField('Update Password')

#This is form for password reset request creator
class PwdResetRequestform(Form):
    emailid = StringField('Your EmailID:-', validators=[Required(), Length(1, 64),Email()])
    submit = SubmitField('Reset Password')

#This form is actually pwd reset using the checking email in the system
class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),Email()])
    password = PasswordField('New Password', validators=[Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

# Before we take request for password we have to confirm email this function will confirm the email address from database
    def validate_email(self,field):
        if SVSuserReg.query.filter_by(email = field.data).first() is None:
            raise ValidationError('Unknown Email Address this email address is not register in our system')


#THis form is used to update user email address in the system
class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[Required(), Length(1, 64),Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if SVSuserReg.query.filter_by(emid=field.data).first():
            raise ValidationError('Email already registered.')




