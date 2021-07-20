#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import flash, redirect, url_for

from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    role = db.Column(db.String(64))
    password_hash = db.Column(db.String(200))

    def __repr__(self):
        return '<User {}>'.format(self.username)  


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@login.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash ('Du musst angemeldet sein...')
    return redirect(url_for('auth.login'))

