# sendosc.sh

# Sendet OSC Kommando
# Kommandozeilen-Parameter:
# --ip=<IP-Adresse des OSC-Servers> oder 127.0.0.1
# --port=<Port des OSC-Servers> oder 8800
# --address=<Adress-String beginnend mit '/'> oder /test
# --value=<Wert> oder ''

codepath="${CLUBDMX_CODEPATH:-/home/pi/clubdmx_code}"
cd $codepath

python3 dmx/sendosc.py $1 $2 $3 $4 $5
