# AI-CORE Local Infrastructure

Infrastruttura locale AI-driven per sviluppare, testare e automatizzare agenti GPT, orchestratori, backup e UI.

## 📂 Struttura

```
ai-core/
├── agents/             # agenti esecutivi (upload, loop)
├── llm/                # modelli Ollama (es. mistral)
├── prompts/            # prompt OpenManus
├── operator/           # engine OpenOperator
├── orchestrator/       # automazioni (es. n8n)
├── dashboard/          # frontend React (opzionale)
├── updater/            # update script
├── instructions/       # task JSON da eseguire
├── logs/               # output agenti
├── config/             # credenziali (es. service_account.json)
```

## ✅ Script inclusi

- `upload_file_to_folder.py` → carica file su Drive (senza duplicati)
- `exec_loop.py` → esegue task periodici automaticamente
- `update_local.sh` → aggiorna componenti modulari

## 🚀 Avvio rapido

```bash
python3 agents/exec_loop.py
```

## 🔐 Escludi file sensibili
Controlla `.gitignore` per mantenere sicura la repo pubblica.

---

> Creato da LUKE_CTO_SAAS – ottimizzato per deploy su Hetzner o locale.
