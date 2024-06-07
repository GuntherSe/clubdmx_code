@echo off
echo Starte ClubDMX...
pushd %~dp0

echo %cd%
rem ins code-Verzeichnis wechseln:
cd ..

rem development oder production:
set FLASK_ENV=production
rem set FLASK_ENV=development

set FLASK_DEBUG=0
set FLASK_APP=wsgi.py

set PYTHONPATH=%cd%\app;%cd%\dmx

set CLUBDMX_ROOMPATH=%cd%\..\clubdmx_rooms

py wsgi.py
REM flask run --host=0.0.0.0 --port=5000

pause
popd
