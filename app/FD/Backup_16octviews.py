from . import FD
from flask import render_template, redirect, request, url_for, flash,Response,session,make_response,send_file
from ..models import SVSIpCamReg,SVSuserReg,SVSFaceTab
from ..email import send_email
from .. import db,login_manager
from datetime import datetime
from cryptography.fernet import Fernet
from flask.ext.login import login_user, logout_user, login_required,current_user
import numpy as np
import cv2
import PIL.Image
import time,random,cPickle
import requests,cStringIO
import threading
import os,io
from PIL import Image
import base64,argparse
from base64 import b64encode
from threading import Thread,ThreadError,Event


class Cam():
    def __init__(self,url):
        self.stream = requests.get(url,stream=True)
        self.thread_cancelled = False
        self.thread = Thread(target=self.run)
        self.count = 0
        self.imgret = Image
        self.strpath = str
        #self.argobj = Parse()
        self.facecascade = cv2.CascadeClassifier("C:\\Users\\IBM_ADMIN\\Desktop\\svsapp\\svsapp\\app\\FD\\haarcascade-frontalface-alt.xml")
        print "camera initialised"

    def start(self):
        self.thread.start()
        print "Camera Stream is started"

    def run(self):

        bytes = ''
        while not self.thread_cancelled:
            try:
                bytes+=self.stream.raw.read(1024)
                a = bytes.find('\xff\xd8')
                b = bytes.find('\xff\xd9')
                if a!=-1 and b!=-1:
                    jpg = bytes[a:b+2]
                    bytes= bytes[b+2:]
                    img = cv2.imdecode(np.fromstring(jpg,dtype=np.uint8),cv2.IMREAD_COLOR)
                    #Create Frame Number for each frame we are assigning the 08d with number which is there in self.count
                    framenumber = '%08d' % (self.count)
                    #set screen color to gray so harr cascade can detect edges and faces
                    screencolor = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                    #customize how cascade detect your face
                    faces = self.facecascade.detectMultiScale(screencolor,scaleFactor = 1.3,minNeighbors=3,minSize = (30,30),flags = cv2.CASCADE_SCALE_IMAGE)
                    # If face length is 0 then it indicate that no faces detected
                    if len(faces) == 0:
                        pass
                        #If faces is detected then it will return 1 or more than 1 depend upon faces
                    elif len(faces) > 0:
                        print('Face Detected')
                        #Graph face and draw rectangle arround it.
                        for (x,y,w,h) in faces:
                            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                            #face= img[x:x+w,y:y+h]
                            self.strpath = "C:\\Users\\IBM_ADMIN\\Desktop\\svsapp\\svsapp\\app\\FD\\FaceCaps\\"
                            self.strpath+=framenumber
                            self.strpath+='.jpg'
                            print self.strpath
                            cv2.imwrite("C:\\Users\\IBM_ADMIN\\Desktop\\svsapp\\svsapp\\app\\FD\\FaceCaps\\" + framenumber + '.jpg',img)
                            #self.imgret = Image.fromarray(img)
                            self.imgret = img
                            #return self.imgret
                            if self.imgret is None:
                                 print 'its none'
                            else:
                                #newimg = cv2.imread(self.strpath)
                                #ennewimg = cv2.imencode(".jpg",self.imgret)
                                #img_str = cv2.imencode('.jpg',newimg)[1].tostring()
                                readbin = open(self.strpath,'rb').read()
                                emid = SVSuserReg.query.filter_by(emid=current_user.emid).first()
                                camid = SVSIpCamReg.query.filter_by(u_id = current_user.id).first()
                                try:
                                    CamImgAdd =  SVSFaceTab(u_id = emid.id,cam_id= camid.u_id,Face_image = readbin)
                                    db.session.add(CamImgAdd)
                                    db.session.commit()
                                except:
                                    print('Exception is generated')
                                print("data is added ")

                            #Increment count so we get uniquename for each frame
                    self.count +=1

            except ThreadError:
                self.thread_cancelled = True

    def is_running(self):
        return self.thread.isAlive()

    def shut_down(self):
        self.thread_cancelled = True
        #block while waiting for thread to terminate
        while self.thread.isAlive():
            time.sleep(1)
        return True


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

        '''for rec in camfaces:
            camfacesimag=rec.Face_image
            #response = make_response(camfacesimag)
            #response.headers["Content-type"] = "image/jpeg"
            #response.headers['Content-Disposition'] = 'attachment; filename=img.jpg'
            #rec.Face_imagenew = response
            rec.Face_imagenew = send_file(io.BytesIO(camfacesimag),attachment_filename='logo.png',mimetype='image/png')
        return render_template('FaceDetect/FaceShow.html',allface = camfaces)'''

    else:
       print("I am in else none")













@FD.route('/FDViewFaces', methods=['GET', 'POST'])
@login_required
def FDViewFaces():
    camtab = SVSIpCamReg.query.filter_by(u_id = current_user.id).first()

    dkey = camtab.key
    bdkey=bytes(dkey)
    f = Fernet(bdkey)
    bcamurl = bytes(camtab.camurl_hash)
    camurl =f.decrypt(bcamurl)
    url=str(camurl)
    if camtab.FDstore == 1:
        emid = SVSuserReg.query.filter_by(emid=current_user.emid).first()
        camid = SVSIpCamReg.query.filter_by(u_id = current_user.id).first()
        camfaces = SVSFaceTab.query.filter_by(cam_id = camid.u_id , u_id = emid.id ).all()


        for rec in camfaces:
            camfacesimag=rec.Face_image
            rec.Face_imagenew = b64encode(camfacesimag)

        return render_template('FaceDetect/FDViewFaces.html',allface = camfaces)


    else:
       print("I am in else none")


