#!/bin/bash

# create flask-socketio website on pythonanywhere

export PYTHONANYWHERE = "true"
cd /home/GuntherSeiser/clubdmx_code
/home/GuntherSeiser/.virtualenvs/clubenv310/bin/gunicorn --worker-class eventlet -w 1  --bind unix:${DOMAIN_SOCKET} wsgi:app'