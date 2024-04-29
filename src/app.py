# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import uuid
import random
import os
from datetime import datetime, timedelta

from pgpy import PGPKey, PGPMessage

import utils
import account_routes
import mail_handler

from mail_handler import register_logger

app = Flask(__name__)

CORS(app)



server_mail_user_name = os.environ.get('server_mail_user_name')
server_sender_mail = os.environ.get('server_sender_mail')
server_mail_user_password = os.environ.get('server_mail_user_password')
smtp_port = os.environ.get('smtp_port')
host = os.environ.get('host')

server_private_key_path = os.environ.get('server_private_key_path')
server_private_key_passphrase = os.environ.get('server_private_key_passphrase')

imap_mail_user_name = os.environ.get('imap_mail_user_name')
imap_mail_password = os.environ.get('imap_mail_password')
imap_host = os.environ.get('host')

if None in [server_private_key_path, server_private_key_passphrase, smtp_port, host, imap_mail_user_name, imap_mail_password]:
    raise ValueError("Nicht alle erforderlichen Umgebungsvariablen sind definiert. Öffnen Sie das Skript export_variable.sh im Verzeichnis testscript und setzen Sie die Werte für alle erforderlichen Umgebungsvariablen.\nNachdem Sie die Werte festgelegt haben, führen Sie das Skript aus!")


@app.route('/create', methods=['POST'])
def create_account_route():
    return account_routes.create_account()


#@app.route('/list', methods=['GET'])
#def list_accounts_route():
    #return account_routes.list_accounts()


@app.route('/login', methods=['POST'])
def login_accounts_route():
    return account_routes.login()

@app.route('/register', methods=['POST'])
def register_key():
    try:
        users_db = utils.load_data()
        data = request.form
        account_id = data.get('account-id')
        password = data.get('password')
        email_address = data.get('email-address')

        user_key_id = data.get('key-id')
        key_id = user_key_id.replace(" ", "")

        register_logger.info(f"Registrierungsanfrage...")

        if not key_id:
            register_logger.error('Ungültige Key-ID bereitgestellt.')
            return jsonify({'error': 'Ungültige Key-ID'}), 400

        if not account_id or not password or not email_address or not key_id:
            register_logger.error('Erforderliche Felder fehlen.')
            return jsonify({'error': 'Fehlende Pflichtfelder'}), 400

        pgp_key_file = request.files.get('pgp-key')
        if not pgp_key_file:
            register_logger.error('PGP-Schlüsseldatei fehlt.')
            return jsonify({'error': 'PGP-Schlüsseldatei ist erforderlich.'}), 400

        # Benutzerdaten überprüfen
        user_data = utils.find_user(account_id, users_db)
        if not user_data:
            register_logger.error('Konto nicht gefunden.')
            return jsonify({'error': 'Konto nicht gefunden!'}), 404

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user_data['hashed_password'] != hashed_password:
            register_logger.error('Authentifizierung fehlgeschlagen.')
            return jsonify({'error': 'Authentifizierung fehlgeschlagen!'}), 401

        #if not utils.verify_email_domain(email_address):
           # register_logger.error('Ungültige E-Mail-Domäne.')
            #return jsonify({'error': 'Ungültige E-Mail-Domäne'}), 400

        


        pgp_key_content = pgp_key_file.read()
        pgp_key, _ = PGPKey.from_blob(pgp_key_content)
        fingerprint = pgp_key.fingerprint

        imported_key_id = str(fingerprint)
        

        if key_id != imported_key_id:
            register_logger.error('Die bereitgestellte Key-ID stimmt nicht mit der des importierten PGP-Schlüssels überein.')
            return jsonify({'error': 'Die bereitgestellte Key-ID entspricht nicht der des importierten PGP-Schlüssels.'}), 400

        # Generierung und Speicherung des Challenge-Tokens mit einer Ablaufszeit von 10 Minuten
        expiration_time = datetime.now() + timedelta(seconds=10*60)
        random_value = str(random.randint(10000, 99999))
        challenge_token = {'token': str(uuid.uuid4()) + '-' + random_value,
                           'expiration_time': expiration_time.isoformat()}
        user_data['challenge_token'] = challenge_token
        user_data['pending_key_fingerprint'] = fingerprint
        user_data['pending_email'] = email_address
        utils.save_data(users_db)

        def is_token_expired():
            return datetime.now() > expiration_time

        registered_keys = user_data.get('registered_keys', {})

        if email_address in registered_keys and key_id in registered_keys[email_address]:
            challenge_email_body = (
                f"Moin {account_id},\n\n"
                f"Schön, dass Sie die Nachricht entschlüsselt haben!\n"
                f"Ihr PGP-Schlüssel mit der Key-ID {key_id} wurde bereits signiert.\n"
                f"Sie können die Signatur jedoch jederzeit aktualisieren, wenn Sie das möchten, antworten Sie bitte auf diese E-Mail mit dem richtigen Challenge-Token im angegebenen Format.\n\n"
                f"Im Betreff Ihrer E-Mail sollte stehen: 'Re: [ACME-PGP] Response'. Zum Beispiel: Re: [ACME-PGP] Response\nIm Text der E-Mail geben Sie bitte folgendes Format ein: "
                f'Challenge-token: "Ihr per E-Mail erhaltenes Token"\n' 'Zum Beispiel: Challenge-token: "94cd2a3c-a8ae-48ae-a461-b7f345736e2b-43711"\n\n'
                f"Sobald Sie mit dem korrekten Token geantwortet haben, ist Ihre Registrierung abgeschlossen. Sie erhalten dann eine Benachrichtigungs-E-Mail, die die erfolgreiche Registrierung Ihres PGP-Schlüssels bestätigt und auch Ihren signierten Schlüssel im Anhang enthält.\n\n"
                f"Ihr Challenge-Token lautet: {challenge_token['token']}\n\n"
                f"Ganz wichtig: Bei der Antwort auf diese E-Mail darf die Nachricht nicht verschlüsselt sein.\n\n"
                f"Vielen Dank für Ihr Verständnis und Ihre Zusammenarbeit.\n\n"
                f"Grüße von Nelly und Jordan\nTeam-06"
            )
        else:
            # Versand der verschlüsselten E-Mail mit dem Challenge-Token und dem vom Benutzer
            # bereitgestellten öffentlichen Schlüssel als Anhang
            challenge_email_body = (
                f"Moin {account_id},\n\n"
                f"Prima! Sie haben die Nachricht entschlüsselt.\n"
                f"Wichtig: Diese Nachricht war verschlüsselt. Sie müssten die Nachricht mit Ihrem privaten Schlüssel entschlüsseln, um zu bestätigen, dass der öffentliche Schlüssel Ihnen gehört. Dazu benötigten Sie Ihren privaten Schlüssel.\n\n"
                f"Um die Registrierung Ihres PGP-Schlüssels abzuschließen, antworten Sie bitte auf diese E-Mail mit dem richtigen Challenge-Token im angegebenen Format.\n\n"
                f"Im Betreff Ihrer E-Mail sollte stehen: 'Re: [ACME-PGP] Response'. Zum Beispiel: Re: [ACME-PGP] Response\nIm Text der E-Mail geben Sie bitte folgendes Format ein: "
                f'Challenge-token: "Ihr per E-Mail erhaltenes Token"\n' 'Zum Beispiel: Challenge-token: "94cd2a3c-a8ae-48ae-a461-b7f345736e2b-43711"\n\n'
                f"Sobald Sie mit dem korrekten Token geantwortet haben, ist Ihre Registrierung abgeschlossen. Sie erhalten dann eine Benachrichtigungs-E-Mail, die die erfolgreiche Registrierung Ihres PGP-Schlüssels bestätigt und auch Ihren signierten Schlüssel im Anhang enthält.\n\n"
                f"Ihr Challenge-Token lautet: {challenge_token['token']}\n\n"

                f"Ganz wichtig: Bei der Antwort auf diese E-Mail darf die Nachricht nicht verschlüsselt sein.\n\n"
                f"Vielen Dank für Ihr Verständnis und Ihre Zusammenarbeit.\n\n"
                f"Grüße von Nelly und Jordan\nTeam-06"
            )

        challenge_message = PGPMessage.new(challenge_email_body)
        encrypted_challenge_email_body = pgp_key.encrypt(challenge_message)

        if not encrypted_challenge_email_body:
            register_logger.error('Fehler beim Verschlüsseln der Challenge-Nachricht.')
            return jsonify({'error': 'Fehler beim Verschlüsseln der Challenge-Nachricht'}), 500

        # Name der Datei für die Speicherung und den E-Mail-Anhang
        filename = f"{account_id}-{email_address}-{key_id}.asc"

        keys_directory = "public_keys_users"
        if not os.path.exists(keys_directory):
            os.makedirs(keys_directory)

        public_keys_path = os.path.join(keys_directory, filename)

        pgp_key_file.seek(0)

        pgp_key_file.save(public_keys_path)

        
        mail_handler.send_email(server_sender_mail, host, smtp_port, email_address, "[ACME-PGP] Register", str(encrypted_challenge_email_body), attachment=public_keys_path)

        # Verarbeitung der E-Mail-Verifizierung
        verification_success = mail_handler.handle_email_verification(
            imap_mail_user_name, imap_mail_password, imap_host, is_token_expired, email_address, user_data, public_keys_path, account_id, imported_key_id, users_db)

        if verification_success:

            if email_address in registered_keys:
                if key_id in registered_keys[email_address]:
                    register_logger.warning('Die bereitgestellte Key-ID ist bereits mit dieser E-Mail-Adresse registriert.')
                else:
                
                    registered_keys[email_address].append(key_id)
                    utils.save_data(users_db)
                    register_logger.info(f"Key-ID zu E-Mail-Adresse hinzugefügt.")
            else:
                registered_keys[email_address] = [key_id]
                utils.save_data(users_db)
                register_logger.info(f"Erste Key-ID für ihre E-Mail-Adresse registriert.")

            register_logger.info('Challenge-Verfahren erfolgreich abgeschlossen. Benachrichtigungs-E-Mail gesendet.')
            return jsonify({'message': 'Challenge-Verfahren erfolgreich abgeschlossen. Benachrichtigungs-E-Mail gesendet.'}), 200
        else:
            register_logger.error('Token ist nicht mehr gültig.')
            del user_data['challenge_token']
            del user_data['pending_key_fingerprint']
            del user_data['pending_email']
            utils.save_data(users_db)
            return jsonify({'error': 'Dein Token ist abgelaufen. Sie haben die Zeit von 10 Minuten überschritten.'}), 400

    except Exception as e:
        register_logger.exception(f"Ein Fehler ist aufgetreten: {str(e)}")
        return jsonify({'error': 'Ein Fehler ist aufgetreten. Bitte überprüfen Sie die Serverprotokolle für weitere Details.'}), 500

if __name__ == '__main__':
    app.run(debug=True)

