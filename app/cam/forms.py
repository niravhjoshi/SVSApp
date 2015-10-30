from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required,Email,URL,EqualTo,Length
from wtforms import StringField,SubmitField,PasswordField,validators,SelectField, ValidationError,BooleanField,RadioField
from ..models import SVSIpCamReg


opt =  ["11*23","22*59","70*80","1080*1920"]
class CamRegister(Form):

    sitename = StringField('Your SiteName:-',validators = [Required(),Length(min=1,max=56)])
    camurl = StringField('Your Ip Cam URL:-',validators = [Required(),URL()])
    sitevis = SelectField("Select Your Visual Size", validators =[Required()],choices=[(f,f) for f in opt])
    FDStore = RadioField('Lable',choices=[('1','Yes Enable Face Detection'),('0','Not Enable Face Detection')])
    Camsubmit = SubmitField('Register')

class Camedit(Form):
    sitename = StringField('Your SiteName:-',validators = [Required(),Length(min=1,max=56)])
    camurl = StringField('Your Ip Cam URL:-',validators = [Required(),URL()])
    sitevis = SelectField("Select Your Visual Size", validators =[Required()],choices=[(f,f) for f in opt])
    FDStore = RadioField('Lable',choices=[('1','Yes Enable Face Detection'),('0','Not Enable Face Detection')])
    Camsubmit = SubmitField('Update Cam')

def validate_ipcam(self, field):
    if SVSIpCamReg.query.filter_by(camurl_hash=field.data).first():
        raise ValidationError('Cam URL is already register with us')

