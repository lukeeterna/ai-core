# ~/Desktop/ai-core/updater/update_local.sh

#!/bin/bash

LOG_FILE=~/Desktop/ai-core/logs/update.log

{
  echo "\n🔁 [$(date)] Avvio update locale..."

  if [ -d "~/Desktop/ai-core/operator/.git" ]; then
    echo "📦 Aggiorno Open-Operator..."
    cd ~/Desktop/ai-core/operator && git pull
  fi

  if [ -d "~/Desktop/ai-core/prompts/.git" ]; then
    echo "📦 Aggiorno OpenManus..."
    cd ~/Desktop/ai-core/prompts && git pull
  fi

  echo "✅ Update completato con successo."
} >> "$LOG_FILE" 2>&1

exit 0
