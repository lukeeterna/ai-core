
# ~/Desktop/ai-core/operator/src/upload_code.py

import os
import zipfile
import subprocess
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
TARGET_DIR = os.path.join(PROJECT_ROOT, 'agents')
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'logs')

os.makedirs(BACKUP_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime('%Y-%m-%d-%H%M')
ZIP_NAME = f"code-backup-{TIMESTAMP}.zip"
ZIP_PATH = os.path.join(BACKUP_DIR, ZIP_NAME)

print(f"📦 Backup in corso: {TARGET_DIR} → {ZIP_PATH}")

with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, PROJECT_ROOT)
            zipf.write(full_path, arcname)

print("✅ Codice zippato con successo.")

subprocess.run(["python3", "agents/upload_file_to_folder.py", "agents", ZIP_PATH])
