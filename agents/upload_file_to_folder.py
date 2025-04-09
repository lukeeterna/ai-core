# ~/Desktop/ai-core/agents/upload_file_to_folder.py

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import sys

# === CONFIG ===
SERVICE_ACCOUNT_FILE = os.path.expanduser('~/Desktop/ai-core/config/service_account.json')
SCOPES = ['https://www.googleapis.com/auth/drive']
PARENT_FOLDER_ID = '16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC'  # ID root cartella Drive

# === INPUT ===
if len(sys.argv) != 3:
    print("❌ Uso: python3 upload_file_to_folder.py <nome_cartella> <file_locale>")
    sys.exit(1)

target_folder = sys.argv[1]
local_file = sys.argv[2]
filename = os.path.basename(local_file)

# === AUTENTICAZIONE ===
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

# === CREA O OTTIENI CARTELLA ===
def get_or_create_folder(name, parent_id):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    folders = results.get('files', [])
    if folders:
        return folders[0]['id']
    metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
    folder = service.files().create(body=metadata, fields='id').execute()
    return folder['id']

# === ELIMINA FILE SE GIA' PRESENTE ===
def delete_if_exists(name, folder_id):
    query = f"name='{name}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    for f in results.get('files', []):
        service.files().delete(fileId=f['id']).execute()

# === UPLOAD FILE ===
def upload_file(local_path, folder_id):
    delete_if_exists(filename, folder_id)
    media = MediaFileUpload(local_path, resumable=True)
    metadata = {'name': filename, 'parents': [folder_id]}
    uploaded = service.files().create(body=metadata, media_body=media, fields='id').execute()
    print(f"✅ File '{filename}' caricato. ID: {uploaded['id']}")

# === EXECUTION ===
target_id = get_or_create_folder(target_folder, PARENT_FOLDER_ID)
upload_file(local_file, target_id)
