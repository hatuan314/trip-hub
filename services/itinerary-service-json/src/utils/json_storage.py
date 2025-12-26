import json
from pathlib import Path
from threading import Lock

lock = Lock()

def read_json(path):
    p = Path(path)
    if not p.exists():
        return []
    with lock, open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with lock, open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
