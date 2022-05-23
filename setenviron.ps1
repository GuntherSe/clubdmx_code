# Umgebungsvariablen setzen:

$env:FLASK_APP="wsgi.py"
$env:FLASK_ENV="development"
$env:PYTHONPATH="$pwd\\app;$pwd\\dmx"
$env:SQLALCHEMY_DATABASE_URI="sqlite:///$pwd\\app.db"
$env:SQLALCHEMY_TRACK_MODIFICATIONS="False"
Write-Host "Umgebungsvariablen gesetzt."

# für den Start von Python:
# flask shell