#!/bin/bash


export server_mail_user_name=''
export server_sender_mail=''
export server_mail_user_password=''
export server_private_key_path='my-private-key.asc'
export smtp_port='25'
export host='mail.itsec-23.sec'

#Ab Hier muss es angepasst werden
#geben Sie das Passwort für den privaten Schlüssel ein: 
export server_private_key_passphrase='Geben Sie Hier Das Passwort der private Schlüssel'

#geben Sie der Username der Imap Server ein
#Beispiel:   export imap_mail_user_name='team06'
export imap_mail_user_name=''

#geben Sie das Passort der imap server ein
#Beispiel: export imap_mail_password='Testpassword'
export imap_mail_password=''
