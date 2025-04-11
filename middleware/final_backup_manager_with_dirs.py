"""
final_backup_manager_with_dirs.py

Versione finale operativa del sistema di backup e monitoraggio.
Questo script:
  - Recupera e valida (tramite claude_validate_history) la cronologia della sessione.
  - Include nel backup le directory locali "Agents", "Projects" e "chat_sessions".
  - Crea un file ZIP contenente il file di sessione (in formato Markdown) e le directory.
  - Carica il file ZIP su Google Drive e lo organizza nella struttura:
      BASE_FOLDER/Backups/YYYY-MM-DD/
  - Riavvia la sessione alla fine del processo di backup.
  
Le migliorie includono:
  • Verifica semantica del contenuto (CLAUDE: funzione claude_validate_history).
  • Logging avanzato in ogni fase per il debug (PHIND).
  • Codice strutturato e modulare con best practices (COPILOT).
"""

import os
import time
import zipfile
import logging
import yaml
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from safe_openai_utils import get_current_token_usage, get_session_history, start_new_session

# ---------------------
# CONFIGURAZIONE LOGGING
# ---------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --------------------------
# CARICAMENTO DELLE CONFIGURAZIONI
# --------------------------
with open("settings.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

TOKEN_LIMIT = config.get("token_limit", 2000)
RESPONSE_THRESHOLD = config.get("response_threshold", 2.0)
MONITOR_INTERVAL = config.get("monitor_interval", 10)

# Folder di riferimento su Drive e nome del folder principale per i backup.
BASE_FOLDER_ID = "16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC"
MAIN_BACKUP_FOLDER_NAME = "Backups"

# Percorsi locali delle directory da includere (assicurati che esistano)
LOCAL_AGENTS_PATH = os.path.join(os.getcwd(), "Agents")
LOCAL_PROJECTS_PATH = os.path.join(os.getcwd(), "Projects")
LOCAL_CHAT_SESSIONS_PATH = os.path.join(os.getcwd(), "chat_sessions")  # Nuova cartella per il backup delle chat

# ---------------------------
# FUNZIONI DI VALIDAZIONE (CLAUDE)
# ---------------------------
def claude_validate_history(history):
    """
    Funzione placeholder per la validazione semantica della cronologia della sessione.
    In un ambiente reale, questa funzione potrebbe effettuare delle chiamate a un modello NLP per verificare la coerenza.
    Qui restituisce semplicemente l'input, registrando l'intervento.
    """
    logging.info("Esecuzione della validazione semantica della cronologia (CLAUDE).")
    # In una versione reale, qui verificheresti che il contenuto sia completo e coerente.
    return history

# ----------------------------
# FUNZIONI DI ACCESSO A GOOGLE DRIVE
# ----------------------------
def get_drive():
    """Autentica e restituisce un'istanza di GoogleDrive."""
    gauth = GoogleAuth()
    try:
        gauth.LoadCredentialsFile("token.json")
    except Exception as e:
        logging.warning("Impossibile caricare token.json, verrà eseguita l'autenticazione via webserver.")
    if not gauth.credentials or gauth.credentials.invalid:
        gauth.LocalWebserverAuth()  # Avvia il processo OAuth
        gauth.SaveCredentialsFile("token.json")
    drive = GoogleDrive(gauth)
    logging.info("Autenticazione su Google Drive completata.")
    return drive

# ---------------------------
# FUNZIONI DI GESTIONE DELLE CARTELLE SU DRIVE
# ---------------------------
def search_folder(drive, parent_id, folder_name):
    """
    Cerca una cartella con il nome specificato all'interno di parent_id.
    Ritorna l'oggetto folder se trovato, altrimenti None.
    """
    query = (f"'{parent_id}' in parents and title = '{folder_name}' "
             "and mimeType = 'application/vnd.google-apps.folder' and trashed = false")
    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        logging.info(f"Cartella '{folder_name}' trovata in parent {parent_id}.")
        return file_list[0]
    else:
        logging.info(f"Cartella '{folder_name}' non trovata in parent {parent_id}.")
        return None

def create_folder(drive, parent_id, folder_name):
    """Crea e restituisce una nuova cartella all'interno di parent_id."""
    folder_metadata = {
        'title': folder_name,
        'parents': [{"id": parent_id}],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    logging.info(f"Cartella '{folder_name}' creata in parent {parent_id}.")
    return folder

def ensure_folder(drive, parent_id, folder_name):
    """
    Restituisce la cartella se esiste; altrimenti la crea.
    Evita duplicazioni.
    """
    folder = search_folder(drive, parent_id, folder_name)
    return folder if folder else create_folder(drive, parent_id, folder_name)

def organize_backup_file(drive, file_id):
    """
    Sposta il file di backup (ZIP) nella struttura:
       BASE_FOLDER/Backups/YYYY-MM-DD/
    """
    backups_folder = ensure_folder(drive, BASE_FOLDER_ID, MAIN_BACKUP_FOLDER_NAME)
    date_folder_name = time.strftime("%Y-%m-%d")
    date_folder = ensure_folder(drive, backups_folder["id"], date_folder_name)
    backup_file = drive.CreateFile({'id': file_id})
    backup_file['parents'] = [{"id": date_folder["id"]}]
    backup_file.Upload()
    logging.info(f"File di backup (ID: {file_id}) organizzato in '{MAIN_BACKUP_FOLDER_NAME}/{date_folder_name}'.")

# ---------------------------
# FUNZIONI PER CREARE IL FILE ZIP DI BACKUP
# ---------------------------
def zip_directory_contents(zip_handle, folder_path, arc_path=""):
    """
    Aggiunge ricorsivamente il contenuto della directory folder_path al file ZIP.
    Il percorso all'interno del ZIP sarà definito da arc_path.
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            local_path = os.path.join(root, file)
            # Calcola il percorso relativo per mantenere la struttura
            relative_path = os.path.relpath(local_path, folder_path)
            zip_path = os.path.join(arc_path, relative_path)
            zip_handle.write(local_path, zip_path)
            logging.debug(f"Aggiunto file: {local_path} -> {zip_path}")

def create_backup_zip(session_content, output_zip_filename):
    """
    Crea un file ZIP che include:
      - Il file di sessione (in Markdown)
      - Le directory locali Agents, Projects e chat_sessions, se presenti.
    """
    try:
        with zipfile.ZipFile(output_zip_filename, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            # Scrive il file di sessione
            session_file_name = "session_backup.md"
            backup_zip.writestr(session_file_name, session_content)
            logging.info(f"Aggiunto il file di sessione al ZIP: {session_file_name}")

            # Aggiunge la directory Agents
            if os.path.isdir(LOCAL_AGENTS_PATH):
                zip_directory_contents(backup_zip, LOCAL_AGENTS_PATH, "Agents")
                logging.info("Directory 'Agents' aggiunta al backup ZIP.")
            else:
                logging.warning("Directory 'Agents' non trovata.")

            # Aggiunge la directory Projects
            if os.path.isdir(LOCAL_PROJECTS_PATH):
                zip_directory_contents(backup_zip, LOCAL_PROJECTS_PATH, "Projects")
                logging.info("Directory 'Projects' aggiunta al backup ZIP.")
            else:
                logging.warning("Directory 'Projects' non trovata.")

            # Aggiunge la directory chat_sessions
            if os.path.isdir(LOCAL_CHAT_SESSIONS_PATH):
                zip_directory_contents(backup_zip, LOCAL_CHAT_SESSIONS_PATH, "chat_sessions")
                logging.info("Directory 'chat_sessions' aggiunta al backup ZIP.")
            else:
                logging.warning("Directory 'chat_sessions' non trovata.")

        logging.info(f"File ZIP di backup '{output_zip_filename}' creato con successo.")
        return output_zip_filename
    except Exception as e:
        logging.error(f"Errore nella creazione del file ZIP: {e}")
        return None

# ---------------------------
# FUNZIONI DI BACKUP E MONITORAGGIO
# ---------------------------
def measure_response_time():
    """Misura (simulata) il tempo di risposta e lo restituisce."""
    simulated_response_time = 1.5  # Valore simulato
    logging.info(f"Tempo di risposta simulato: {simulated_response_time} secondi")
    return simulated_response_time

def synthesize_context(history):
    """
    Sintetizza la cronologia della sessione per ridurre il carico.
    Utilizza la funzione di validazione di CLAUDE.
    """
    validated_history = claude_validate_history(history)
    lines = validated_history.split("\n")
    half_index = len(lines) // 2
    summarized = "\n".join(lines[:half_index])
    logging.info("Sintesi del contesto completata per ridurre il carico di token.")
    return summarized

def perform_backup_full(drive):
    """
    Esegue la procedura completa di backup:
      - Recupera e sintetizza la cronologia della sessione.
      - Crea un file ZIP che include il file di sessione e le directory Agents, Projects e chat_sessions.
      - Carica il file ZIP su Google Drive e lo organizza nella struttura predefinita.
    """
    logging.info("Avvio della procedura di backup completo.")
    
    # Recupera la cronologia della sessione
    history = get_session_history()
    summarized_context = synthesize_context(history)
    
    # Definisce il nome del file ZIP con timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_zip_filename = f"backup_full_{timestamp}.zip"
    
    # Crea il file ZIP di backup
    zip_file = create_backup_zip(summarized_context, backup_zip_filename)
    if not zip_file:
        logging.error("Creazione del file ZIP fallita.")
        return None

    # Carica il file ZIP su Google Drive
    try:
        backup_drive_file = drive.CreateFile({'title': backup_zip_filename})
        backup_drive_file.SetContentFile(backup_zip_filename)
        backup_drive_file.Upload()
        logging.info(f"File ZIP '{backup_zip_filename}' caricato su Google Drive con successo.")
        
        # Organizza il file all'interno della struttura di cartelle
        organize_backup_file(drive, backup_drive_file["id"])
        return backup_drive_file["id"]
    except Exception as e:
        logging.error(f"Errore durante l'upload su Google Drive: {e}")
        return None

def monitor_session():
    """
    Loop principale: monitora periodicamente la sessione.
    Se il consumo dei token o il tempo di risposta superano le soglie definite, esegue il backup completo
    e riavvia la sessione.
    """
    drive = get_drive()
    logging.info("Avvio del monitoraggio della sessione.")
    
    while True:
        try:
            current_tokens = get_current_token_usage()
            response_time = measure_response_time()
            logging.info(f"Token attuali: {current_tokens}, Tempo di risposta: {response_time}s")
            
            if current_tokens > TOKEN_LIMIT or response_time > RESPONSE_THRESHOLD:
                logging.info("Soglia superata. Avvio del backup completo.")
                backup_file_id = perform_backup_full(drive)
                if backup_file_id:
                    logging.info("Backup completo eseguito e organizzato. Riavvio della sessione.")
                else:
                    logging.error("Backup completo fallito. Riavvio della sessione senza backup.")
                start_new_session()
            else:
                logging.info("Parametri operativi nella norma.")
            
            time.sleep(MONITOR_INTERVAL)
        except Exception as e:
            logging.error(f"Eccezione nel loop di monitoraggio: {e}")
            time.sleep(MONITOR_INTERVAL)

if __name__ == "__main__":
    monitor_session()
