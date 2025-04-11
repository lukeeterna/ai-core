# ~/Desktop/ai-core/agents/backup_project.py

import shutil
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ZIP_NAME = f"full-backup-{datetime.now().strftime('%Y-%m-%d-%H%M')}.zip"
ZIP_PATH = os.path.join(BASE_DIR, "logs", ZIP_NAME)

print(f"📦 Backup dell’intero progetto ai-core → {ZIP_PATH}")

shutil.make_archive(ZIP_PATH.replace(".zip", ""), 'zip', BASE_DIR)

print("✅ Completato.")
