# Umgebungsvariablen setzen:
# DIESES SCRIPT SO AUFRUFEN: . setenviron.bash

export FLASK_APP=wsgi.py
export FLASK_ENV=development
export PYTHONPATH="${PWD}/app:${PWD}/dmx"
# c:\Users\Gunther\OneDrive\Programmierung\clubdmx_code\app;c:\Users\Gunther\OneDrive\Programmierung\clubdmx_code\dmx
export SQLALCHEMY_DATABASE_URI="sqlite:///${PWD}/app.db"
export SQLALCHEMY_TRACK_MODIFICATIONS="False"
echo "Umgebungsvariablen gesetzt."
# flask db init
# flask db migrate -m "users table"
# flask db upgrade

# für den Start von Python:
# flask shell
