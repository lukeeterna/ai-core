# Middleware DeepSeek con Backup su Google Drive

## Panoramica
Questo progetto integra un middleware basato su DeepSeek eseguito su Ollama per:
- Monitorare il consumo dei token e il tempo di risposta.
- Eseguire il backup automatico della sessione in formato Markdown.
- Caricare il backup su Google Drive utilizzando PyDrive.

I moduli sono arricchiti con controlli, logging dettagliato e placeholder per interventi avanzati (verifica logica con CLAUDE, analisi e debug con PHIND, e completamento del codice con COPILOT).

## Contenuti
- `deepseek_middleware.py`: Loop di monitoraggio e gestione del backup.
- `google_drive_utils.py`: Gestione dell’autenticazione e dell’upload su Google Drive.
- `safe_openai_utils.py`: Funzioni di simulazione per il monitoraggio della sessione.
- `credentials.json`: Credenziali per l’accesso a Google Drive.
- `settings.yaml`: Configurazione dei parametri operativi.
- `requirements.txt`: Dipendenze Python necessarie.

## Istruzioni
1. **Configura le credenziali:**  
   Modifica `credentials.json` con le tue credenziali di Google.

2. **Imposta i parametri operativi:**  
   Verifica e, se necessario, modifica i parametri in `settings.yaml`.

3. **Installa le dipendenze:**
   ```bash
   pip install -r requirements.txt
