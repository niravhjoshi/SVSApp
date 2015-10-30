from . import FD
from flask import render_template, redirect, request, url_for, flash,Response,session,make_response,send_file
from ..models import SVSIpCamReg,SVSuserReg,SVSFaceTab,current_app
from ..email import send_email
from .. import db,login_manager
from datetime import datetime
from cryptography.fernet import Fernet
from flask.ext.login import login_user, logout_user, login_required,current_user
import numpy as np
import cv2
from celery import Celery
import PIL.Image
import time,random,cPickle
import requests,cStringIO
import threading
import os,io
from PIL import Image
import base64,argparse
from base64 import b64encode
from threading import Thread,ThreadError,Event
#from manage import app

#This is calling view for the class which will call class and load
@FD.route('/FDStart', methods=['GET', 'POST'])
@login_required

def FDStart():
    camtab = SVSIpCamReg.query.filter_by(u_id = current_user.id).first()

    dkey = camtab.key
    bdkey=bytes(dkey)
    f = Fernet(bdkey)
    bcamurl = bytes(camtab.camurl_hash)
    camurl =f.decrypt(bcamurl)
    url=str(camurl)
    if camtab.FDstore == 1:
        cam = Cam(url)
        #cam.start()
        cam.run()
        emid = SVSuserReg.query.filter_by(emid=current_user.emid).first()
        camid = SVSIpCamReg.query.filter_by(u_id = current_user.id).first()
        camfaces = SVSFaceTab.query.filter_by(cam_id = camid.u_id , u_id = emid.id ).all()

    else:
       print("I am in else none")

@FD.route('/FDViewFaces', methods=['GET', 'POST'])
@login_required
def FDViewFaces():
        emid = SVSuserReg.query.filter_by(emid=current_user.emid).first()

        page = request.args.get('page', 1, type=int)
        pagination = SVSFaceTab.query.filter_by( u_id = emid.id ).order_by(SVSFaceTab.Face_save_date.desc()).paginate(page, per_page=current_app.config['SVS_PAGE_PHOTO'],error_out=False)
        photos = pagination.items


        for rec in photos:
            camfacesimag=rec.Face_image
            rec.Face_imagenew = b64encode(camfacesimag)

        return render_template('FaceDetect/FDViewFaces.html',allface = photos,pagination = pagination)


