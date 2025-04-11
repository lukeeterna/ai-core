# 📂 File: context_recovery_system.py

"""
Sistema integrato per il recupero del contesto AI-driven
Versione completa che collega:
- DeepSeek locale via middleware
- Estensione Chrome per ChatGPT
- Gestione conversazioni e backup
"""

import os
import json
import time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === CONFIG ===
SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ['https://www.googleapis.com/auth/drive']
BACKUP_SOURCE_FOLDER = "/root/ai-core/logs"
DRIVE_FOLDER_NAME = "chat-backups"
CONTEXT_STATE_FILE = "context_state.json"
SUMMARY_FILENAME = "session_summary.json"

# === DRIVE UTILS ===
def init_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def upload_file_to_drive(service, folder_id, filepath):
    filename = os.path.basename(filepath)
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaFileUpload(filepath, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# === CONTEXT CHECKER ===
def detect_context_loss(text):
    indicators = ["non ricordo", "non so", "puoi ripetere", "non ho abbastanza informazioni"]
    return any(indicator in text.lower() for indicator in indicators)

def load_context_state():
    if os.path.exists(CONTEXT_STATE_FILE):
        with open(CONTEXT_STATE_FILE) as f:
            return json.load(f)
    return {}

def save_context_state(state):
    with open(CONTEXT_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def generate_summary_log():
    return {
        "timestamp": datetime.now().isoformat(),
        "paths": [BACKUP_SOURCE_FOLDER],
        "tools": ["DeepSeek", "Claude", "Phind", "Copilot"],
        "status": "Contesto operativo in corso."
    }

# === EXEC LOOP ===
def exec_loop():
    print("🔁 Controllo in corso...")
    context = load_context_state()
    last_message = context.get("last_message", "")

    with open("last_chat.txt") as f:
        current_message = f.read()

    if detect_context_loss(current_message):
        print("⚠️ Perdita contesto rilevata. Generazione backup...")
        summary = generate_summary_log()
        with open(SUMMARY_FILENAME, 'w') as f:
            json.dump(summary, f, indent=2)

        # Salvataggio su Drive
        service = init_drive_service()
        folder_id = get_or_create_folder(service, DRIVE_FOLDER_NAME)
        upload_file_to_drive(service, folder_id, SUMMARY_FILENAME)

        print("✅ Backup caricato su Drive.")
        context['last_message'] = current_message
        save_context_state(context)
    else:
        print("✅ Nessuna perdita di contesto.")

if __name__ == "__main__":
    while True:
        exec_loop()
        time.sleep(180)  # ogni 3 minuti
