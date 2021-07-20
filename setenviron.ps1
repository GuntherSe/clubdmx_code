# Umgebungsvariablen setzen:

$env:FLASK_APP="wsgi.py"
$env:FLASK_ENV="development"
$env:PYTHONPATH="$pwd\\app;$pwd\\dmx"
# c:\Users\Gunther\OneDrive\Programmierung\clubdmx_code\app;c:\Users\Gunther\OneDrive\Programmierung\clubdmx_code\dmx
$env:SQLALCHEMY_DATABASE_URI="sqlite:///$pwd\\app.db"
$env:SQLALCHEMY_TRACK_MODIFICATIONS="False"
Write-Host "Umgebungsvariablen gesetzt."
# flask db init
# flask db migrate -m "users table"
# flask db upgrade

# für den Start von Python:
# flask shell