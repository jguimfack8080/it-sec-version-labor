# -*- coding: utf-8 -*-
import imaplib
import email
from email import policy
import re
import time
import utils
import os
import time
import imaplib
import email
from email import policy
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from smtplib import SMTP
from logger import setup_logger

register_logger = setup_logger('register_key_logger', 'Logs/register/register-{date}.log')

def handle_email_verification(imap_mail_user_name, imap_mail_password, imap_host, is_token_expired, email_address, user_data, public_keys_path, account_id, imported_key_id, users_db):
    try:
        register_logger.info("Starte IMAP...")
        #IMAP auf Port 143 ohne TLS
        imap = imaplib.IMAP4(imap_host, 143)
        imap.login(imap_mail_user_name, imap_mail_password)
        imap.select('inbox')

        while not is_token_expired():
            tmp, messages = imap.search(None, 'ALL')
            messages = messages[0].split()[::-1]

            for num in messages:
                tmp, data = imap.fetch(num, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email, policy=policy.default)

                if msg['Subject'] == 'Re: [ACME-PGP] Response':
                    sender_email = msg['From']

                    if sender_email:
                        if sender_email == email_address:
                            payload = ""
                            for part in msg.walk():
                                if part.get_content_type() == 'text/plain':
                                    payload += part.get_payload(decode=True).decode('utf-8')
                            match = re.search(r'Challenge-token: "(.*?)"', payload)
                            if match:
                                token_value = match.group(1)
                                # Vergleich der Tokens aus der E-Mail mit dem in der Datenbank vorhandenen Token
                                if token_value == user_data['challenge_token']['token']:
                                    utils.sign_and_export_key(
                                        public_keys_path, account_id, email_address, imported_key_id)
                                    del user_data['challenge_token']
                                    del user_data['pending_key_fingerprint']
                                    del user_data['pending_email']
                                    utils.save_data(users_db)
                                    return True  
                                else:
                                    time.sleep(1)
                        else:
                            print("Die E-Mail-Adresse des Absenders ", sender_email,
                                "ist unterschiedlich von der Registrierungsadresse: ", email_address)
                    else:
                        print("Die E-Mail-Adresse des Absenders konnte nicht gefunden werden.")

        imap.close()
        imap.logout()

    except Exception as e:
        register_logger.exception(f"Fehler bei der E-Mail-Verifizierung: {str(e)}")


def send_email(sender_email, smtp_host, smtp_port, recipient, subject, body, attachment=None):
    try:
        register_logger.info("Mail Senden...")

        if recipient is None or sender_email is None:
            raise ValueError("Die E-Mail-Anmeldeinformationen sind nicht festgelegt.")

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        if attachment:
            with open(attachment, "rb") as file:
                part = MIMEApplication(
                    file.read(), Name=os.path.basename(attachment))
                part["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(attachment)}"'
                )
                message.attach(part)

        with SMTP(smtp_host, smtp_port) as smtp:
            smtp.sendmail(sender_email, recipient, message.as_string())

    except Exception as e:
        register_logger.exception(f"Fehler beim Senden der E-Mail: {str(e)}")

