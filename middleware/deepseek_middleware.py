import logging
import os
from middleware.safe_openai_utils import evaluate_session_status
from env_loader import get_env_variable

logging.basicConfig(level=logging.INFO)


def monitor_and_decide_backup(context: dict) -> bool:
    """
    Valuta se effettuare il backup in base al contesto ricevuto:
    token usage, response time o errori rilevati.
    """
    try:
        token_threshold = int(get_env_variable("TOKEN_THRESHOLD", 1500))
        latency_threshold = float(get_env_variable("LATENCY_THRESHOLD", 2.0))

        token_usage = context.get("token_usage", 0)
        latency = context.get("response_time", 0.0)
        crash_detected = context.get("error_detected", False)

        logging.info("[MW] Contesto ricevuto → token: %s, latenza: %s, errore: %s",
                     token_usage, latency, crash_detected)

        if crash_detected:
            logging.warning("[MW] Rilevato crash AI → trigger backup")
            return True

        if token_usage >= token_threshold:
            logging.info("[MW] Token sopra soglia (%s)", token_threshold)
            return True

        if latency >= latency_threshold:
            logging.info("[MW] Latenza sopra soglia (%s)", latency_threshold)
            return True

        logging.info("[MW] Nessun criterio soddisfatto per backup")
        return False

    except Exception as e:
        logging.error("[MW] Errore nel middleware: %s", str(e))
        return False
