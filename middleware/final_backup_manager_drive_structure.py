import os
import datetime
import logging
from middleware.google_drive_utils import upload_file_to_drive
from env_loader import get_env_variable

logging.basicConfig(level=logging.INFO)


def create_local_backup() -> str:
    """
    Simula la creazione di un file di backup locale.
    Restituisce il path del file creato.
    """
    try:
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, "w") as f:
            f.write("Backup automatico eseguito.")
        logging.info("[BACKUP] File di backup creato: %s", filepath)
        return filepath
    except Exception as e:
        logging.error("[BACKUP] Errore creazione file locale: %s", str(e))
        return ""


def main():
    filepath = create_local_backup()
    if filepath:
        filename = os.path.basename(filepath)
        success = upload_file_to_drive(filepath, filename)
        if success:
            logging.info("[BACKUP] Backup caricato su Google Drive con successo.")
        else:
            logging.error("[BACKUP] Fallito caricamento su Google Drive.")
    else:
        logging.error("[BACKUP] Nessun file da caricare.")


if __name__ == "__main__":
    main()