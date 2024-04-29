#!/bin/bash

BASE_URL="http://127.0.0.1:5000"
USER_DB_FILE="users_db.json"
#rm $USER_DB_FILE

# Test des Endpunkts zum Erstellen eines Kontos
echo -e "Teste den Endpunkt zum Erstellen eines Kontos... \n"
curl -X POST -H "Content-Type: application/json" -d '{"account-id": "testuser", "password": "Passworduser-It-@Sicherheit@2024"}' "$BASE_URL/create"


# Test des Endpunkts zum Auflisten von Konten
#echo -e "Teste den Endpunkt zum Auflisten von Konten...\n\n"
#curl -X GET "$BASE_URL/list"

# Test des Anmelde-Endpunkts
echo -e "\nTeste den Anmelde-Endpunkt...\n"
curl -X POST -F "account-id=testuser" -F "password=Passworduser-It-@Sicherheit@2024" "$BASE_URL/login"

# Test des Endpunkts zum Registrieren eines Schlüssels
echo -e "\n\nTeste den Endpunkt zum Registrieren eines Schlüssels..."

#Beispiel: curl -X POST -F "account-id=testuser" -F "password=Passworduser-It-@Sicherheit@2024" -F "email-address=team06@mail.itsec-23.sec" -F "key-id=G146 3AA8 CA97 D6F0 2U64 661A Z0E9 DEC8 502C 21F9" -F "pgp-key=@./testkey.asc" "$BASE_URL/register"
curl -X POST -F "account-id=testuser" -F "password=Passworduser-It-@Sicherheit@2024" -F "email-address=team06@mail.itsec-23.sec" -F "key-id=" -F "pgp-key=@./test-server-pub-key.asc" "$BASE_URL/register"
echo

