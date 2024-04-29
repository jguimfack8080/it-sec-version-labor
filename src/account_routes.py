from flask import request, jsonify
import hashlib
import uuid
import utils
import re
from logger import setup_logger

create_logger = setup_logger('create_logger', 'Logs/create/create-{date}.log')
login_logger = setup_logger('login_logger', 'Logs/login/login-{date}.log')


def create_account():
    create_logger.info("Erstellung eines Benutzerkonto...")
    users_db = utils.load_data()
    data = request.json
    original_account_id = data.get("account-id")
    password = data.get("password")

    if not original_account_id or not password:
        create_logger.error("Konto-ID und Passwort sind erforderlich")
        return jsonify({"error": "Konto-ID und Passwort sind erforderlich"}), 400

    if original_account_id in users_db:
        create_logger.warning("Es existiert schon ein Konto mit diesem Konto-ID")
        return (
            jsonify({"error": "Es existiert schon ein Konto mit diesem Konto-ID"}),
            409,
        ) 

    if len(password) < 16:
        create_logger.error("Das Passwort muss mindestens 16 Zeichen lang sein")
        return (
            jsonify({"error": "Das Passwort muss mindestens 16 Zeichen lang sein"}),
            400,
        )
    if not re.search(r"[A-Z]", password):
        create_logger.error("Das Passwort muss mindestens einen Großbuchstaben enthalten")
        return (
            jsonify(
                {"error": "Das Passwort muss mindestens einen Großbuchstaben enthalten"}
            ),
            400,
        )
    if not re.search(r"[a-z]", password):
        create_logger.error("Das Passwort muss mindestens einen Kleinbuchstaben enthalten")
        return (
            jsonify(
                {
                    "error": "Das Passwort muss mindestens einen Kleinbuchstaben enthalten"
                }
            ),
            400,
        )
    if not re.search(r"\d", password):
        create_logger.error("Das Passwort muss mindestens eine Zahl enthalten")
        return (
            jsonify({"error": "Das Passwort muss mindestens eine Zahl enthalten"}),
            400,
        )
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        create_logger.error("Das Passwort muss mindestens ein Sonderzeichen enthalten")
        return (
            jsonify(
                {"error": "Das Passwort muss mindestens ein Sonderzeichen enthalten"}
            ),
            400,
        )

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    modified_account_id = str(uuid.uuid5(
        uuid.NAMESPACE_DNS, original_account_id))

    user_data = {
        "original_account_id": original_account_id,
        "hashed_password": hashed_password,
        "modified_account_id": modified_account_id,
        "registered_keys": {},  # Initialize an empty dictionary for registered keys
    }

    users_db[original_account_id] = user_data
    utils.save_data(users_db)

    create_logger.info('Konto erfolgreich erstellt!')
    return (
        jsonify(
            {
                "account-id": original_account_id,
                "modified-account-id": modified_account_id,
            }
        ),
        201,
    )


def login():
    login_logger.info('Anmeldung Versuch...')
    users_db = utils.load_data()  # Laden der Benutzerdatenbank
    data = request.form
    account_id = data.get("account-id")
    password = data.get("password")

    # Überprüfen, ob Konto-ID und Passwort bereitgestellt wurden
    if not account_id or not password:
        login_logger.error('Konto-ID und Passwort sind erforderlich')
        return jsonify({"error": "Konto-ID und Passwort sind erforderlich"}), 400

    # Suche nach dem Benutzer in der Datenbank
    user_data = utils.find_user(account_id, users_db)
    if not user_data:
        login_logger.error('Konto nicht gefunden')
        return jsonify({"error": "Konto nicht gefunden"}), 404

    # Überprüfung des Passworts
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user_data["hashed_password"] != hashed_password:
        login_logger.error('Authentifizierung fehlgeschlagen')
        return (
            jsonify({"error": "Authentifizierung fehlgeschlagen"}),
            401,
        )

    login_logger.info('Anmeldung erfolgreich')
    return jsonify({"message": "Erfolgreich angemeldet"}), 200


