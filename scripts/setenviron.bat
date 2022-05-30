rem Umgebungsvarialblen setzen:

set FLASK_APP=wsgi.py
set FLASK_ENV=production
set PYTHONPATH=c:\Users\Gunther\OneDrive\Programmierung\clubdmx_code\app;c:\Users\Gunther\OneDrive\Programmierung\clubdmx_code\dmx
set SQLALCHEMY_DATABASE_URI=sqlite:///c:\Users\Gunther\OneDrive\Programmierung\clubdmx_code\app.db
set SQLALCHEMY_TRACK_MODIFICATIONS=False

rem flask db init
rem flask db migrate -m "users table"
rem flask db upgrade

rem für den Start von Python:
rem flask shell

