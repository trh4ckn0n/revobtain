#!/bin/bash
# Listener simple via socat sur le port 4444

PORT=4444
LOGFILE=connections.log

# Nettoyage précédent
rm -f $LOGFILE

echo "[*] Starting listener on port $PORT..."
socat TCP-LISTEN:$PORT,reuseaddr,fork - > $LOGFILE &
