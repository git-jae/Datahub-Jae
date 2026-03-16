import json
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).parent / "auditoria.jsonl"

def registrar(usuario, categoria, quantidade, status="success", detalhe=""):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps({"timestamp": datetime.now().isoformat(timespec="seconds"),
            "usuario": usuario, "categoria": categoria, "quantidade": quantidade,
            "status": status, "detalhe": detalhe}, ensure_ascii=False) + "\n")

def listar_logs(limit=500):
    if not LOG_PATH.exists():
        return []
    records = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try: records.append(json.loads(line.strip()))
            except: pass
    return records[-limit:]
