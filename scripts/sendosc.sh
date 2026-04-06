# sendosc.sh

# Sendet OSC Kommando
# Kommandozeilen-Parameter:
# --ip=<IP-Adresse des OSC-Servers> oder -i <IP-Adresse> , default: 127.0.0.1
# --port=<Port des OSC-Servers> oder -p <Port> , default: 8800
# --address=<Adress-String beginnend mit '/'> oder -a <Adresse> , default /test
# --value=<Wert> , default ''

# Beispiele: ./sendosc.sh -i 192.168.0.10 -a /exefader -e 1 0.5

codepath="${CLUBDMX_CODEPATH:-/home/pi/clubdmx_code}"
cd $codepath

python3 scripts/sendosc.py $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11} ${12}
