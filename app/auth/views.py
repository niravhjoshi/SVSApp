#This is auth app views file
from . import  auth
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required,current_user
from .forms import LoginForm,UserRegForm,ChangePwdform,PasswordResetForm,PwdResetRequestform,ChangeEmailForm
from ..email import send_email
from .. import db,login_manager
from datetime import datetime
from ..models import SVSuserReg
from cryptography import fernet

@auth.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfimed.html')

#This route will register for new user in system for firsttime

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegForm()
    if form.validate_on_submit():
        dbusr = SVSuserReg(fname=form.fname.data,lname=form.lname.data,emid=form.em.data,mob=form.mob.data,password=form.pwd.data)
        db.session.add(dbusr)
        db.session.commit()
        token = dbusr.generate_confirmation_token()
        em = form.em.data
        #send_email(em,'Account confirmation Email form SVS','mail/auth/confirm',user=form.em.data,token=token)
        send_email(em, 'Confirm Your Account','mail/auth/confirm', user=form.fname.data, token=token)

        flash("Mail Sent you .Please activate your ID using the Link in Email '{}'".format(form.em.data))
        return redirect(url_for('auth.login'))
    return render_template('auth/UserRegister.html', form=form)

#This route is email confirmation link sent to user after registration done this link is external link which can be accessible from email
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

#This route is used when use try to resend confirmation email if he /she did not received it.
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.emid, 'Confirm Your Account',
               'mail/auth/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

#This route is called when register user try to login that time this view function decorator will be called

@auth.route('/login',methods =['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        emid = SVSuserReg.query.filter_by(emid=form.email.data).first()
        if emid is not None and emid.verify_password(form.lpwd.data):
            login_user(emid,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username and Password..!!!')
    return render_template('auth/Login.html',form=form)

#This route will be called when logged in user want to update their password from old password to new password

@auth.route('/changepwd',methods = ['GET','POST'])
@login_required
def changepwd():
    form = ChangePwdform()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_pwd.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash("Your Password has been updated")
            return  redirect(url_for('main.index'))
        else:
            flash("Your Password Invalid")
    return  render_template('auth/change_pwd.html',form=form)


# This route will be called when use officialy logged out from site.
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


#This route will be called when user want to reset password since user may not be logged in hence he want to reset its password
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form =PwdResetRequestform()
    if form.validate_on_submit():
        useremail=SVSuserReg.query.filter_by(emid = form.emailid.data).first()

        if useremail:
            token = useremail.generate_reset_token()
            send_email(useremail.emid,'SVS App RESET Your Password','mail/auth/pwdreset',user=useremail.fname,token=token,next=request.args.get('next'))
            flash('An Email has sent you to reset your password ')
        flash('Your email is invalid please check youe email')
        return redirect(url_for('auth.login'))
    return render_template('auth/pwdreset.html',form=form)

# THis route will be used when use will click on reset link which he/she got in email
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = SVSuserReg.query.filter_by(emid=form.email.data).first()
        if user is None:
            flash("User is invalid or link is not working")
            return redirect(url_for('main.index'))

        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/pwdreset.html', form=form)

#This route will allow you to change the user email address inside the database this form will render the form and send email token confirmation link.
@auth.route('/change_email',methods =['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            newemail = form.email.data
            token = current_user.generate_email_change_token(newemail)
            send_email(form.email.data,'Confirm Your Email Update','mail/auth/change_em',user = current_user.fname,token = token)
            flash('We have send email to your new email address please check on activation {0}'.format(newemail))
            return redirect(url_for('main.index'))

        else:
            flash('Invalid email id or password ')
    return render_template('auth/change_email.html',form=form)

#This route will confirm token link from email and validate email and update user new email address in the database.
@auth.route('/change_ema/<token>')
@login_required
def change_ema(token):
    if current_user.change_email(token):
        flash('Your email address has been updated fine....')
    else:
        flash('This request is invalid')
    return redirect(url_for('main.index'))
