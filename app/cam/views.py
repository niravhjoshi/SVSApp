from . import cam
from flask import render_template, redirect, request, url_for, flash,Response,session
from flask.ext.login import login_user, logout_user, login_required,current_user
from ..models import SVSIpCamReg,SVSuserReg
from .forms import CamRegister,Camedit
from ..email import send_email
from .. import db,login_manager
from datetime import datetime
from camera import VideoCamera
from cryptography.fernet import Fernet


@cam.route('/Camregister', methods=['GET', 'POST'])
@login_required
def Camregister():
    form = CamRegister()
    if form.validate_on_submit():
        fkey = Fernet.generate_key()
        f = Fernet(fkey)
        ecamurl = f.encrypt(bytes(form.camurl.data))
        emid = SVSuserReg.query.filter_by(emid=current_user.emid).first()
        CamRef = SVSIpCamReg(camusername=emid,sitename =form.sitename.data,camurl_hash =ecamurl,key=fkey,sview=form.sitevis.data,FDstore = form.FDStore.data)
        db.session.add(CamRef)
        flash('Your cam has been added now.')
        return redirect(url_for('main.index'))
    return render_template('cam/IpCamReg.html', form=form)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#This link will stream from camera and convert it into jpeg and stream it

@cam.route('/stream')
@login_required
def stream():
    return Response(gen(VideoCamera()),mimetype='multipart/x-mixed-replace; boundary=frame')

#This link will show html which has img tag and source of it will be stream
@cam.route('/live')
@login_required
def live():
    return render_template('cam/stream.html')



#This route will show your camera list for loged in user
@cam.route('/listallcams')
@login_required
def listallcams():
   camtab = SVSIpCamReg.query.filter_by(u_id = current_user.id).all()
   for rec in camtab:
      dkey = rec.key
      bdkey=bytes(dkey)
      f = Fernet(bdkey)
      bcamurl = bytes(rec.camurl_hash)
      camurl =f.decrypt(bcamurl)
      rec.camurlnew = camurl

   return render_template('cam/viewallcam.html',allcam = camtab)

#This route will edit your camera url site and size in your
@cam.route('/editcams/<int:id>',methods=['GET','POST'])
def editcams(id):
    camedit = SVSIpCamReg.query.get_or_404(id)
    form = Camedit()
    if form.validate_on_submit():
        camedit.sitename = form.sitename.data
        fkey = Fernet.generate_key()
        f = Fernet(fkey)
        ecamurl = f.encrypt(bytes(form.camurl.data))
        camedit.key = fkey
        camedit.camurl_hash = ecamurl
        camedit.sview = form.sitevis.data
        camedit.FDstore = form.FDStore.data
        db.session.add(camedit)
        flash("Your Camera has been updated")
        return redirect(url_for('.listallcams'))
    form.sitename.data = camedit.sitename
    dkey = camedit.key
    bdkey=bytes(dkey)
    f = Fernet(bdkey)
    bcamurl = bytes(camedit.camurl_hash)
    camurl =f.decrypt(bcamurl)
    form.camurl.data = camurl
    form.sitevis.data = camedit.sview
    form.FDStore.data = str(camedit.FDstore)
    return render_template('cam/editcam.html',form=form)


