# Implementierung eines automatisierten PGP-Schlüssel-Signaturdienstes mit SMTP-Kommunikation und Datenhaltung

Diese Anwendung ermöglicht die einfache Verwaltung von PGP-Schlüsseln über eine Webanwendung mit automatischer Signierung und Validierung.

## Inhaltsverzeichnis

1. [Voraussetzungen](#voraussetzungen)
2. [Installation](#installation)
3. [Verwendung](#verwendung)
4. [API-Endpunkte](#api-endpunkte)
5. [Beispielanwendungen](#beispielanwendungen)
6. [Mitwirkende](#mitwirkende)

## Voraussetzungen

Um diese Anwendung auszuführen, benötigen Sie:

- Python 3.x
- Flask
- flask_cors 
- pgpy
- dnspython
- Sie müssen mit dem Hochschulnetzwerk verbunden sein (entweder über Eduroam oder Sie können das VPN nutzen).Da unser Mailserver mit unserem Hochschul-Account läuft.

## Installation

1. Klonen Sie dieses Repository auf Ihren lokalen Computer. (https://github.com/jguimfack8080/Version1.0-IT.git)
2. Navigieren Sie in das Verzeichnis der Anwendung. Im diesem Verzeichnis, wo sich diese Readme.md Datei befindet.
3. Führen Sie das Setup-Skript `setupenvironnement.sh` mit Root-Rechten aus, um die erforderlichen Pakete zu installieren: `sudo bash testscript/setupenvironnement.sh`
- python3
- python3-pip
- python3-venv
- nginx
4. Installieren Sie die erforderlichen Python-Bibliotheken mit `pip install -r requirements.txt`.
5. VPN Einrichtung `https://orientierung.hs-bremerhaven.de/download/Einrichtung_eines_Cisco_AnyConnect_VPN-Clients-23.pdf`


## Verwendung
**Hinweis:** Alle Shell Skripte befinden sich im Verzeichnis testscript.
1. Bevor Sie die Anwendung ausführen, müssen Sie Ihre Werte für die folgenden Umgebungsvariablen im Skript `export_variable.sh` festlegen. Dies ist ein sehr wichtiger Schritt für das reibungslose Funktionieren der Anwendung:

   - `server_mail_user_name`: Der Benutzername für das E-Mail-Konto, das zum Versenden von E-Mails verwendet wird.
   - `server_sender_mail`: Die E-Mail-Adresse, von der aus E-Mails gesendet werden sollen.
   - `server_mail_user_password`: Das Passwort für das E-Mail-Konto, das zum Versenden von E-Mails verwendet wird.
   - `server_private_key_path`: Der Pfad zur privaten PGP-Schlüsseldatei, die für die Signierung von E-Mails verwendet wird.
   - `server_private_key_passphrase`: Das Passwort für Ihren privaten Schlüssel, das zum Signieren von Schlüsseln benötigt wird.

   Führen Sie das Skript mit dem Befehl `source testscript\export_variable.sh` aus, um die Umgebungsvariablen zu setzen.

2. Führen Sie die Anwendung aus, indem Sie das Skript `deploy.sh` oder `deploybackground.sh` ausführen.
   - Mit `deploy.sh` wird die Anwendung im Vordergrund bereitgestellt.
   - Mit `deploybackground.sh` wird die Anwendung im Hintergrund bereitgestellt.
     **Hinweis:** Die Skripte mussen am besten außerhalb des Verzeichnisses `testscript` ausgeführt werden, da sonst möglicherweise eine Fehlermeldung angezeigt wird, dass die Datei `app.py` nicht gefunden wurde (z.B. `bash testscript/deploy.sh` oder `bash testscript/deploybackground.sh`).

3. Ab diesem Zeitpunkt können Sie auf die verschiedenen Endpunkte zugreifen, indem Sie die URL `http://localhost:5000` gefolgt von dem Namen des Endpunkts eingeben und die Anfrage ausführen. Zum Beispiel für den Endpunkt "create" verwenden Sie die URL `http://localhost:5000/create` und genauso für die anderen Endpunkte.



## API-Endpunkte

### 1. `/create`

Erstellt ein neues Benutzerkonto.

**Methode:** POST

**Parameter:**
- `account-id` (string): Die ID des Benutzerkontos.
- `password` (string): Das Passwort für das Benutzerkonto.

**Antworten:**
- Erfolg (201 Created): Das Benutzerkonto wurde erfolgreich erstellt.
- Fehler (400 Bad Request): Ein oder mehrere Pflichtfelder fehlen.
- Konflikt (409 Conflict): Ein Benutzerkonto mit der angegebenen ID existiert bereits.


### . `/login`

Authentifiziert einen Benutzer.

**Methode:** POST

**Parameter:**
- `account-id` (string): Die ID des Benutzerkontos.
- `password` (string): Das Passwort für das Benutzerkonto.

**Antworten:**
- Erfolg (200 OK): Die Authentifizierung war erfolgreich.
- Fehler (400 Bad Request): Ein oder mehrere Pflichtfelder fehlen.
- Nicht gefunden (404 Not Found): Das Benutzerkonto wurde nicht gefunden.
- Nicht autorisiert (401 Unauthorized): Die Authentifizierung ist fehlgeschlagen.

### . `/register`

Registriert einen PGP-Schlüssel für einen Benutzer und startet den Validierungsprozess.

**Methode:** POST

**Parameter:**
- `account-id` (string): Die ID des Benutzerkontos.
- `password` (string): Das Passwort für das Benutzerkonto.
- `email-address` (string): Die E-Mail-Adresse des Benutzers.
- `key-id` (string): Die ID des PGP-Schlüssels.
- `pgp-key` (file): Die PGP-Schlüsseldatei als Anhang.

**Antworten:**
- Erfolg (200 OK): Die Registrierung wurde erfolgreich gestartet und eine E-Mail mit einem Challenge-Token wurde an die angegebene E-Mail-Adresse gesendet.
- Fehler (400 Bad Request): Ein oder mehrere Pflichtfelder fehlen oder der PGP-Schlüssel ist ungültig.
- Nicht gefunden (404 Not Found): Das Benutzerkonto wurde nicht gefunden.
- Nicht autorisiert (401 Unauthorized): Die Authentifizierung ist fehlgeschlagen.

Der Benutzer muss zunächst die E-Mail mithilfe seines privaten Schlüssels entschlüsseln, der zu seinen angehängten PGP-Schlüsseln gehört. Anschließend muss er auf die E-Mail mit dem richtigen Challenge-Token antworten, um die Registrierung abzuschließen. Nach erfolgreicher Validierung wird eine Benachrichtigungs-E-Mail mit dem signierten PGP-Schlüssel als Anhang gesendet.


## Testskript (check.sh)

Um die Funktionalität der Anwendung zu überprüfen, kann das Bash-Skript `check.sh` verwendet werden. Dieses Skript führt eine Reihe von Curl-Befehlen aus, um die verschiedenen Endpunkte der API zu testen.
**Hinweis**: Das Skript muss außer das Verziechnis testscript ausgeführt werden (Beispiel ./testscript/check.sh)

Das Skript verwendet die folgenden Umgebungsvariablen:
- `BASE_URL`: Die Basis-URL der API.
- `USER_DB_FILE`: Der Dateiname der Benutzerdatenbank.

Das Skript führt die folgenden Tests durch:
1. Test des Endpunkts zum Erstellen eines Benutzerkontos.
2. Test des Endpunkts zum Auflisten von Benutzerkonten.
3. Test des Endpunkts zur Anmeldung.
4. Test des Endpunkts zum Registrieren eines PGP-Schlüssels.

## Beispielanwendungen

Sie können die mitgelieferten Beispieldateien verwenden, um die Funktionalität der API-Endpunkte zu testen. Kopieren Sie dazu zunächst Ihre PGP-Schlüsseldatei in dieses Verzeichnis, von wo aus Sie die Anwendung nutzen möchten.

Wenn Sie das Skript `check.sh` verwenden möchten, vergessen Sie nicht, zunächst ein Konto mit Ihren eigenen Informationen zu erstellen und dann beim Endpunkt "register" die Parameter entsprechend anzupassen, indem Sie Ihre eigenen Werte für die folgenden Parameter eingeben:

**Parameter:**
- `account-id` (string): Ihre Account-ID, mit der Sie Ihr Konto erstellt haben.
- `password` (string): Das dazugehörige Passwort.
- `email-address` (string): Ihre E-Mail-Adresse (Stellen Sie sicher, dass Sie Zugriff darauf haben und diese mit einem E-Mail-Client wie Thunderbird verknüpft ist).
- `pgp-key` (file): Ihre PGP-Schlüsseldatei (oder den korrekten Pfad zu Ihrer PGP-Schlüsseldatei).
- `key-id` (string): Die Key-ID Ihres angehängten PGP-Schlüssels (Stellen Sie sicher, dass es sich um die Key-ID des von Ihnen angehängten Schlüssels handelt).


## Mitwirkende

- Nelly Lesly Matchio Kuete (nmatchiokuete@smail.hs-bremerhaven.de)
- Jordan Guimfack Jeuna (jguimfackjeuna@smail.hs-bremerhaven.de)

