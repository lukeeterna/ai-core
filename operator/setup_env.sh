# setup_env.sh
#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  echo "OPENAI_API_KEY=sk-..." > .env
  echo ".env creato. Inserisci la tua chiave."
fi

echo "✅ Ambiente pronto. Ora puoi eseguire:"
echo "python3 deepseek_middleware.py"

---