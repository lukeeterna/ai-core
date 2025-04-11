# ~/Desktop/ai-core/agents/upload_file_to_folder.py

from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import sys

SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
ROOT_FOLDER_ID = '16ilWwbaFk6Zj0ssInwPImYCzz_9b0BXC'  # GPT_BACKUP_ROOT

if len(sys.argv) < 3:
    print("❌ Uso: python3 upload_file_to_folder.py <subfolder> <file_path> [drive]")
    sys.exit(1)

SUBFOLDER_NAME = sys.argv[1]
FILE_PATH = sys.argv[2]

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('drive', 'v3', credentials=creds)

def create_or_get_folder(name, parent_id):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id)").execute()
    folders = results.get('files', [])
    if folders:
        return folders[0]['id']

    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=metadata, fields='id').execute()
    return folder.get('id')

def upload_file_to_folder(file_path, folder_id):
    filename = os.path.basename(file_path)

    # Cerca se esiste già
    query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
    existing = service.files().list(q=query, fields="files(id)").execute().get('files', [])

    # Elimina vecchio file se presente
    for file in existing:
        service.files().delete(fileId=file['id']).execute()

    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ File '{filename}' caricato. ID: {uploaded.get('id')}")


if __name__ == "__main__":
    from googleapiclient.http import MediaFileUpload

    print(f"🚀 Backup file: {FILE_PATH} → sottocartella: {SUBFOLDER_NAME}")
    subfolder_id = create_or_get_folder(SUBFOLDER_NAME, ROOT_FOLDER_ID)
    upload_file_to_folder(FILE_PATH, subfolder_id)
