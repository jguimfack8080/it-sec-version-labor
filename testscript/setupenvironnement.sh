#!/bin/bash

echo "Überprüfe und Installiere Voraussetzungen..."

# Liste der zu installierenden Pakete
pakete=("python3" "python3-pip" "python3-venv" "nginx")

# Schleife durch die Pakete
for paket in "${pakete[@]}"; do
    if dpkg -s $paket &> /dev/null; then
        echo "$paket ist bereits installiert."
    else
        echo "Installiere $paket..."
        sudo apt update
        sudo apt install -y $paket

        if [ $? -eq 0 ]; then
            echo "$paket wurde erfolgreich installiert."
        else
            echo "Fehler beim Installieren von $paket."
        fi
    fi
done
