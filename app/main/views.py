from datetime import datetime
from flask import render_template, Response,abort,flash,redirect,url_for
from . import main
from ..models import SVSuserReg,SVSFaceTab,SVSIpCamReg
from flask.ext.login import login_user, logout_user, login_required,current_user
from flask import render_template, redirect, request, url_for, flash,Response,session,make_response,send_file
from .forms import EditProfileForm
from .. import db,login_manager
from cryptography.fernet import Fernet
from app import create_app,db
from ..add import CallFaceDetectSave

@main.route('/')
@main.route('/index')
@main.route('/Index')
#This your view
def index():
    CallFaceDetectSave()
    return render_template('index.html',current_time = datetime.utcnow())



@main.route('/user/<emid>')
def user(emid):
    user = SVSuserReg.query.filter_by(emid=emid).first_or_404()
    return render_template('user.html',user =user)

#Upong sucessfull submit this sucess form will be called.
@main.route('/sucess')
def sucess():
    return  render_template('Sucess.html')


#This function will display your profile information in the form and if changes are done and it will save changes to db and re render form with updated data.
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.fname = form.Firstname.data
        current_user.lname = form.LastName.data
        current_user.mob = form.mobile.data
        db.session.add(current_user)
        flash("Your Profile has been updated")
        return redirect(url_for('.user',emid =current_user.emid))
    form.Firstname.data = current_user.fname
    form.LastName.data = current_user.lname
    form.mobile.data = current_user.mob
    return render_template('edit-profile.html',form=form)
