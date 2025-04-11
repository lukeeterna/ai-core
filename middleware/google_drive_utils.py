import os
import logging
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from env_loader import get_env_variable

logging.basicConfig(level=logging.INFO)

def authenticate_drive():
    try:
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("middleware/token.json")

        if gauth.credentials is None:
            logging.error("[DRIVE] Credenziali mancanti. Autenticazione fallita.")
            return None

        if gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        gauth.SaveCredentialsFile("middleware/token.json")
        drive = GoogleDrive(gauth)
        logging.info("[DRIVE] Autenticazione completata.")
        return drive

    except Exception as e:
        logging.error("[DRIVE] Errore autenticazione: %s", str(e))
        return None


def upload_file_to_drive(filepath: str, filename: str) -> bool:
    drive = authenticate_drive()
    if not drive:
        return False

    try:
        folder_id = get_env_variable("BACKUP_FOLDER_ID")
        if not folder_id:
            raise ValueError("[DRIVE] Variabile BACKUP_FOLDER_ID mancante nel .env")

        file_drive = drive.CreateFile({
            'title': filename,
            'parents': [{'id': folder_id}]
        })
        file_drive.SetContentFile(filepath)
        file_drive.Upload()

        logging.info("[DRIVE] File '%s' caricato su Drive.", filename)
        return True

    except Exception as e:
        logging.error("[DRIVE] Errore upload: %s", str(e))
        return False
