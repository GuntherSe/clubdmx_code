#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from auth.models import User

role_choices = [("basic", "Basic"),
                # ("guest", "Gast-nicht verwenden!"),
                ("standard", "Standard"),
                ("admin", "Administrator")]

def userbeautify (inputlist:list) -> list:
    """ User-Liste zum Anzeigen in HTML
    statt role wird role_choices[1] angezeigt 
    """
    roledict = dict(role_choices)
    userlist = [{"username":user.username, "role":roledict[user.role]} \
        for user in inputlist]
    # for user in inputlist:
    #     userlist.append ({"username":user.username, "role":roledict[user.role]})
    return userlist


class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    # submit = SubmitField('Log In')



class RegistrationForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    # email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'Wiederhole Passwort', validators=[DataRequired(), EqualTo('password')])
    role = SelectField ("Kategorie", # [DataRequired()],
                        default="basic",
                        choices=role_choices)
    # submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Wähle einen anderen Benutzernamen, dieser existiert bereits.')


class EditForm (FlaskForm):
    username = SelectField('Benutzername', coerce=int)
    role = SelectField ("Rolle", [DataRequired()],
                       choices=role_choices)
    # text = StringField ("Text")
    # password = PasswordField('Neues Passwort', validators=[DataRequired()])
    # password2 = PasswordField(
    #     'Wiederhole Passwort', validators=[DataRequired(), EqualTo('password')])
    # submit = SubmitField('Änderungen speichern')


class PasswordForm (FlaskForm):
    # oldpassword = PasswordField ("altes Passwort", validators=[DataRequired()])
    password = PasswordField('neues Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'wiederhole Passwort', validators=[DataRequired(), EqualTo('password')])
