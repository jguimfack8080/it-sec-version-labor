#!/bin/bash

source testscript/export_variable.sh 
echo "Einrichtung der virtuellen Umgebung..."
python3 -m venv .
source bin/activate


echo "Installieren der Python-Abhängigkeiten..."

pip install Flask flask_cors gnupg PGPy dnspython

echo "Deployement lauft ..."
python src/app.py

if [ $? -eq 0 ]; then

    echo "Die Anwendung läuft jetzt. Zugriff unter http://127.0.0.1:5000/"
else
   echo "Fehler beim Deployement!"

fi
