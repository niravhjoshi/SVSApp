# coding=utf-8
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.login import UserMixin
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from cryptography import fernet
#from . import auth
#This is model class for user registration forum please check.

class SVSuserReg(UserMixin,db.Model):
    __tablename__ = 'SVS_UserReg'
    id = db.Column(db.Integer,primary_key =True)
    fname = db.Column(db.String(64), nullable=False)
    lname = db.Column(db.String(90),nullable = False)
    emid = db.Column(db.String(100),unique=True,index = True)
    cdate = db.Column(db.DateTime,default = datetime.utcnow())
    ladate = db.Column(db.DateTime,default = datetime.utcnow())
    mob = db.Column(db.Integer,unique =True,nullable =False)
    confirmed = db.Column(db.Boolean,default = False)
    pwd_hash = db.Column(db.String(256))
    camreg=db.relationship('SVSIpCamReg', backref='camusername', lazy='dynamic')
    #This is ref table for camid to FaceDetect
    userpid=db.relationship('SVSFaceTab', backref='userid', lazy='dynamic')

    #this method is only writable method hence if it is trying to read it will give an error not readable attribute.
    @property
    def password(self):
        raise AttributeError('Password is not readable attribute')
    #this is set method for function password where we will get hash generated
    @password.setter
    def password(self,password):
        self.pwd_hash = generate_password_hash(password)

    #This method is used to verify hashed password
    def verify_password(self,lpwd):
        return check_password_hash(self.pwd_hash,lpwd)

    #This method will generate token which will be included in the email
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})
    #This function will be called when you have clicked on email url and it will validate URL and if it is valid it will update active field
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


#THis will generate password reset token
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

# This function will generate password reset
    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

#This function wil change email address of the register user and also help you to send confirmation email with token and user need to confirm token
    def generate_email_change_token(self,newemail,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'change_email': self.id,'newemail':newemail})

#THis function will verify email confirmation link along with user password and then update the email address link
    def change_email(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        newemail = data.get('newemail')
        if newemail is None:
            return False
        if self.query.filter_by(emid = newemail).first() is not None:
            return False
        self.emid = newemail
        db.session.add(self)
        return True

#This function will update last activity times stamp in database whenever user access it will show when was user last active.
    def ping(self):
        try:
            self.ladate = datetime.utcnow()
            db.session.add(self)
        except:
            db.session.rollback(self)



    def __repr__(self):
        return '<User %r>' % self.id


#User load method to check if user is there or not
@login_manager.user_loader
def load_user(user_id):
    return SVSuserReg.query.get(int(user_id))


class SVSIpCamReg(db.Model):
    __tablename__ = 'SVS_IpCamReg'
    id = db.Column(db.Integer,primary_key =True)
    u_id = db.Column(db.Integer,db.ForeignKey('SVS_UserReg.id'),nullable=False)
    sitename = db.Column(db.String(100),nullable =False)
    camregdate = db.Column(db.DateTime,default = datetime.utcnow())
    sview = db.Column(db.String(50),nullable = False)
    FDstore = db.Column(db.Integer(),nullable = False)
    camurl_hash = db.Column(db.String(256),nullable =False,unique = False)
    key = db.Column(db.String(256),nullable =False,unique = True)
    #This is ref table for camid to FaceDetect
    campid=db.relationship('SVSFaceTab', backref='camid', lazy='dynamic')


    def __repr__(self):
        return '<Role %r>' % self.id


#This is another table which will save data if we have detect face in the camera it will crop face and store it in the db.
class SVSFaceTab(db.Model):
    __tablename__ = 'SVSFacesTab'
    id = db.Column(db.Integer,primary_key = True)
    u_id  = db.Column(db.Integer,db.ForeignKey('SVS_UserReg.id'),nullable=False)
    cam_id = db.Column(db.Integer,db.ForeignKey('SVS_IpCamReg.id'),nullable = False)
    Face_save_date = db.Column(db.DateTime,default = datetime.utcnow())
    Face_image = db.Column(db.Binary,nullable = False)

    def __repr__(self):
        return '<Role %r>' %self.Face_save_date

