import os
import json
import dns.resolver

import pgpy
from pgpy.constants import SignatureType

from mail_handler import send_email, register_logger

from app import server_sender_mail, server_mail_user_name, server_mail_user_password, server_private_key_path, server_private_key_passphrase, host, smtp_port



json_db_file = "users_db.json"

def load_data():
    if os.path.exists(json_db_file):
        with open(json_db_file, "r") as file:
            data = json.load(file)
            # print("Loaded data:", data)
            return data
    return {}


def save_data(data):
    with open(json_db_file, "w") as file:
        json.dump(data, file, indent=4)


def find_user(account_id, users_db):
    return users_db.get(account_id)


def verify_email_domain(email_address):
    domain = email_address.split('@')[1]
    try:
        dns.resolver.query(domain, 'MX')
        return True
    except dns.exception.DNSException:
        #print("Die Domäne existiert nicht.")
        return False


def sign_and_export_key(public_key_path, user_account_id, email_address, key_Id):
    try:
        private_key_path = server_private_key_path
        output_dir = 'signedKey'
        output_path = os.path.join(
            output_dir, f"signed-key-{user_account_id}-{key_Id}.asc")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        my_private_key, _ = pgpy.PGPKey.from_file(private_key_path)

        private_key_passphrase = server_private_key_passphrase
        assert my_private_key.is_protected

        with my_private_key.unlock(private_key_passphrase):
            user_public_key, _ = pgpy.PGPKey.from_file(public_key_path)

            for user_id in user_public_key.userids:
                signature = my_private_key.certify(
                    user_id, pgpy.constants.SignatureType.Positive_Cert)

                user_id |= signature

        # Speicherung des signierten öffentlichen Schlüssel.
        with open(output_path, 'w') as f:
            f.write(str(user_public_key))

        #print(f"Der öffentliche Schlüssel wurde signiert und gespeichert in... '{output_path}'")

        notification_email_body = f"Moin {user_account_id},\n\nIhre PGP-Schlüsselregistrierung wurde erfolgreich abgeschlossen. \n\nIm Anhang finden Sie Ihren signierten Schlüssel. \n\n\nGrüße von Nelly und Jordan\nTeam-06"

        send_email(server_sender_mail, host, smtp_port, email_address, "[ACME-PGP] Registrierung erfolgreich",
                       notification_email_body, attachment=output_path)
        register_logger.info("Schlüssel erfolgreich signiert und per Mail geschickt")
    except Exception as e:
        
        register_logger.error(f"Ein Fehler ist aufgetreten: {str(e)}")

