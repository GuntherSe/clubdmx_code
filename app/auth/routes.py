#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from auth import auth
from auth.models import User, load_user
from auth.forms import LoginForm, RegistrationForm, EditForm, PasswordForm
from auth.forms import userbeautify

from apputils import standarduser_required, admin_required, redirect_url

# ----------------------------------------------------------------------


# --- login -------------------------------------------------------------

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == "basic":
            return redirect(url_for('basic.exec'))    
        return redirect(url_for('basic.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Ungültiger Benutzername oder Passwort', category="danger")
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # basic-User hat immer Editmode select:
        # if user.role == "basic":
        session["editmode"] = "select" # default für alle Rollen
        # session.permanent = True
        return redirect(redirect_url())

    return render_template('auth/login.html', title='Login', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('basic.index'))



@auth.route('/register', methods=['GET', 'POST'])
@login_required
@standarduser_required
def register():
    """ Neuen User in Datenbank registrieren 

    Abhängig von current_user kann die neue user.role festgelegt
    werden, der neue user kann keine höherwertige role bekommen.
    """
    form = RegistrationForm()

    if request.method == 'POST':
        if request.form["submit_button"] != "true": # schließen-Button
            # return  redirect (url_for ("basic.index"))
            return  redirect (redirect_url ())
        elif    form.validate ():                   # Daten ok
            user = User(username=form.username.data)
            user.set_password(form.password.data)

            # user.role:
            if current_user.role == "admin":
                user.role = form.role.data
            else:
                if form.role.data == "guest":
                    user.role = "guest"
                else:
                    user.role = "standard"

            db.session.add(user)
            db.session.commit()
            flash(f'OK, neuer Benutzer {user.username} ({user.role}) wurde angelegt!')
            return redirect (redirect_url ())
            # return redirect (url_for ("auth.register"))
    return render_template('auth/register.html', title='Register', form=form)


@auth.route('/usermanager', methods=['GET', 'POST'])
@login_required
@admin_required
def usermanager ():
    """ Benutzerdaten ändern 
    """

    form = EditForm()

    if request.method == 'POST':
        eduser = load_user (form.username.data)
        if  request.form["submit_button"] == "laden":
            return  redirect (url_for ("auth.usermanager", eduser=eduser.username))

        elif request.form["submit_button"] == "new":
            nexturl = url_for ("auth.usermanager")
            return redirect (url_for ("auth.register", next=nexturl))


        elif request.form["submit_button"] == "delete":
            if eduser != current_user and eduser.username != "gunther":
                db.session.delete (eduser)
                db.session.commit ()
                flash (f"Benutzer {eduser.username} wurde gelöscht.")
            else:
                flash (f"{eduser.username} kannst du nicht löschen.", 
                    category="danger")
            return redirect(url_for('auth.usermanager'))

        elif request.form["submit_button"] == "pwreset": # Passwort reset 
            nexturl = url_for ("auth.usermanager")
            return redirect (url_for ("auth.password", user=eduser.username,
                    next=nexturl))

        elif  request.form["submit_button"] == "save":
            eduser.role = form.role.data
            db.session.commit()
            flash('Änderungen wurden gespeichert.')
            return redirect(url_for('auth.usermanager', eduser=eduser.username))

        else: # schließen
            return  redirect (url_for ("basic.index"))
        
    users = User.query.order_by(User.username).all () 
    ulist = []
    for u in users:
        ulist.append ((u.id, u.username))
    form.username.choices = ulist
    userview = userbeautify (users)

    edusername = request.args.get ("eduser")
    if not edusername:
        edusername=current_user.username
    eduser = User.query.filter_by(username=edusername).first()
    form.username.default = eduser.id 

    if eduser.role:
        form.role.default = eduser.role
    form.process()

    return render_template ("auth/usermanager.html", 
                form = form, 
                users = userview,
                eduser = eduser)


@auth.route('/password', methods=['GET', 'POST'])
@login_required
def password ():
    """ Passwort ändern 
    """
    form = PasswordForm()
    # if form.validate_on_submit():
    if request.method == 'POST':
        if request.form["submit_button"] != "true": # schließen-Button
            return  redirect (url_for ("basic.index"))
        elif    form.validate ():                   # Daten ok
            # Admin kann fremde logins setzen:
            if "user" in request.args:
                username = request.args["user"]
            else:
                username = current_user.username
            user = User.query.filter_by(username=username).first()
            user.set_password(form.password.data)
            db.session.commit()
            flash('Passwort wurde geändert.')
            # return redirect(url_for('basic.index'))
            return redirect (redirect_url())

    edusername = request.args.get ("user")
    if edusername:
        if current_user.role != "admin":
            flash("nur Admins können fremde Logins setzen.")
            edusername=current_user.username
    else:
        edusername=current_user.username
    return render_template('auth/password.html', title='Passwort ändern', 
                          form=form,
                          user = edusername)


@auth.route ("/userlist")
@login_required
@standarduser_required
def userlist ():
    """ Benutzerliste
    """
    # users = User.query.all ()
    users = User.query.order_by(User.username).all () 
    userlist = userbeautify (users)
    return render_template ("auth/userlist.html", users=userlist)



        