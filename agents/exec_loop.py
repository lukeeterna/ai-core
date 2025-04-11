import os
import time
import zipfile
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === CONFIG ===
SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ['https://www.googleapis.com/auth/drive']
SOURCE_FOLDER = "output"
DRIVE_FOLDER_NAME = "n8n-test"
LOG_FILE = "logs/exec.log"
SUMMARY_FILE = "logs/session_summary.json"
CHECK_INTERVAL = 180

# === INIT SERVICE ===
def init_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

# === GOOGLE DRIVE UPLOAD ===
def get_or_create_drive_folder(service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def zip_and_upload(service, folder_id, zip_name, folder_path):
    zip_path = f"{zip_name}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
    file_metadata = {
        'name': os.path.basename(zip_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(zip_path, resumable=True)
    uploaded = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ Backup uploaded: {uploaded['id']}")

# === CONTEXT RECOVERY ===
def check_context_loss():
    if not os.path.exists(LOG_FILE):
        print("⚠️ exec.log missing, triggering context recovery...")
        generate_summary()
        trigger_backup()
        return

    with open(LOG_FILE, 'r') as f:
        content = f.read()
        if not content.strip():
            print("⚠️ Empty exec.log detected, triggering context recovery...")
            generate_summary()
            trigger_backup()

# === SUMMARY GENERATION ===
def generate_summary():
    summary = {
        "status": "RECOVERY_TRIGGERED",
        "timestamp": datetime.utcnow().isoformat(),
        "note": "DeepSeek detected context loss. Backup initialized."
    }
    with open(SUMMARY_FILE, 'w') as f:
        json.dump(summary, f, indent=4)
    print("📝 Summary written.")

# === BACKUP WRAPPER ===
def trigger_backup():
    service = init_service()
    folder_id = get_or_create_drive_folder(service, DRIVE_FOLDER_NAME)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_and_upload(service, folder_id, f"backup_{timestamp}", SOURCE_FOLDER)

# === MAIN EXEC LOOP ===
if __name__ == "__main__":
    print("🔁 Inizio monitoraggio DeepSeek...")
    while True:
        check_context_loss()
        time.sleep(CHECK_INTERVAL)
