# ~/Desktop/ai-core/agents/exec_loop.py

import os
import time
import json
import subprocess

INSTRUCTION_DIR = os.path.expanduser("~/Desktop/ai-core/instructions")
LOG_FILE = os.path.expanduser("~/Desktop/ai-core/logs/agent-loop.log")
UPLOAD_SCRIPT = os.path.expanduser("~/Desktop/ai-core/agents/upload_file_to_folder.py")


def log(msg):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"[LOOP] {msg}\n")


def process_instruction(file_path):
    with open(file_path) as f:
        instruction = json.load(f)
    if instruction.get("action") == "upload":
        folder = instruction.get("folder")
        filepath = instruction.get("file")
        if folder and filepath and os.path.exists(filepath):
            subprocess.run(["python3", UPLOAD_SCRIPT, folder, filepath])
            log(f"✅ Upload eseguito: {filepath} → {folder}")
        else:
            log(f"❌ Istruzione malformata o file non trovato: {file_path}")


if __name__ == "__main__":
    log("🔁 Avvio ciclo automatico agenti GPT")
    while True:
        try:
            for filename in os.listdir(INSTRUCTION_DIR):
                if filename.endswith(".json"):
                    path = os.path.join(INSTRUCTION_DIR, filename)
                    process_instruction(path)
                    os.remove(path)
        except Exception as e:
            log(f"❌ Errore esecuzione ciclo: {e}")
        time.sleep(60)  # 1 minuto tra un ciclo e l'altro