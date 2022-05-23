# Umgebungsvariablen setzen:
# DIESES SCRIPT SO AUFRUFEN: . setenviron.sh

export FLASK_APP=wsgi.py
export FLASK_ENV=development
export PYTHONPATH="${PWD}/app:${PWD}/dmx"
export SQLALCHEMY_DATABASE_URI="sqlite:///${PWD}/app.db"
export SQLALCHEMY_TRACK_MODIFICATIONS="False"
echo "Umgebungsvariablen gesetzt."
# flask db init
# flask db migrate -m "users table"
# flask db upgrade

# für den Start von Python:
# flask shell
