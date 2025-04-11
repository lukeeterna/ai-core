import sys
import os
import logging
import subprocess
import json
from flask import Flask, request, jsonify, send_file

# Fix path per import da root project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from middleware.safe_openai_utils import evaluate_session_status
from middleware.deepseek_middleware import monitor_and_decide_backup
from env_loader import get_env_variable
from json_logger import setup_json_logger

app = Flask(__name__)

# Inizializza logging
setup_json_logger()
logging.basicConfig(level=get_env_variable("LOG_LEVEL", "INFO"))

# === CONFIG ===
BACKUP_SCRIPT_PATH = "middleware/final_backup_manager_drive_structure.py"
LOG_FILE_PATH = "logs/ai_core.jsonl"


def run_backup():
    try:
        result = subprocess.run([
            "python", BACKUP_SCRIPT_PATH
        ], text=True, capture_output=True, check=True)
        logging.info("[BACKUP] Eseguito: %s", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logging.error("[BACKUP] Errore: %s", e.stderr)
        return False


def fallback_claude(session_context):
    logging.warning("[FALLBACK] Claude in azione...")
    # Placeholder per Claude API
    return {"status": "fallback_claude_attivato", "context": session_context}


@app.route("/trigger", methods=["POST"])
def trigger_monitoring():
    try:
        session_context = request.json
        logging.info("[ORCH] Contesto ricevuto: %s", session_context)

        decision = evaluate_session_status(session_context)
        if decision.get("action") == "backup":
            logging.info("[ORCH] Trigger backup confermato")
            
            if monitor_and_decide_backup(session_context):
                logging.info("[ORCH] Middleware ha autorizzato backup")
                if run_backup():
                    return jsonify({"status": "backup_completato"}), 200
                else:
                    logging.error("[ORCH] Errore in fase di backup")
                    return jsonify({"status": "errore_backup"}), 500
            else:
                return jsonify({"status": "nessun_backup_nel_middleware"}), 200

        return jsonify({"status": "nessun_backup_necessario"}), 200

    except Exception as e:
        logging.exception("[ORCH] Errore trigger: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"orchestrator": "online", "version": "1.0.0"}), 200


@app.route("/logs", methods=["GET"])
def get_logs():
    try:
        if not os.path.exists(LOG_FILE_PATH):
            return jsonify({"error": "File di log non trovato."}), 404
        return send_file(LOG_FILE_PATH, mimetype='text/plain')
    except Exception as e:
        logging.error("[LOGS] Errore lettura log: %s", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
