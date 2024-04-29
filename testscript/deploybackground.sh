#!/bin/bash
source testscript/export_variable.sh 
python3 -m venv .
source bin/activate
pip install Flask flask_cors gnupg PGPy dnspython


echo "Deployement lauft ..."
#python App/app.py

# Anwendung im Hintergrund ausführen
nohup python src/app.py &

if [ $? -eq 0 ]; then
    echo "Die Anwendung wird jetzt im Hintergrund ausgeführt."
    echo "Sie können dieses Terminal schließen, und die Anwendung wird weiterhin ausgeführt."
else
    echo "Fehler beim Deployment!"
fi
