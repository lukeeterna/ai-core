# ~/Desktop/ai-core/updater/update_local.sh

#!/bin/bash

LOG_FILE=~/Desktop/ai-core/logs/update.log

{
  echo "\n🔁 [$(date)] Avvio update locale..."

  echo "📦 Installazione/aggiornamento pacchetti Python..."
  source ~/Desktop/ai-core/.venv/bin/activate
  pip install --upgrade pip
  pip install -r ~/Desktop/ai-core/requirements.txt

  if [ -d "~/Desktop/ai-core/operator/.git" ]; then
    echo "📦 Aggiorno Open-Operator..."
    cd ~/Desktop/ai-core/operator && git pull
  else
    echo "📦 Open-Operator gestione manuale"
  fi

  if [ -d "~/Desktop/ai-core/prompts/.git" ]; then
    echo "📦 Aggiorno OpenManus..."
    cd ~/Desktop/ai-core/prompts && git pull
  else
    echo "📦 Open-Manus gestione manuale"
  fi

  echo "🤖 Aggiorno modello DeepSeek con Ollama..."
  ollama pull deepseek-coder:latest

  echo "🔄 Riavvio orchestratore n8n via Docker..."
  cd ~/Desktop/ai-core/orchestrator
  docker compose up -d

  echo "✅ Update completato con successo."
} >> "$LOG_FILE" 2>&1

exit 0
