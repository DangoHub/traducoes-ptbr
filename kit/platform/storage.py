"""JSON persistence with atomic writes (temp file + replace)."""
import datetime
import json
import os


def load_json(path, default=None):
    if not os.path.isfile(path):
        return default
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def read_text(path, default=""):
    if not os.path.isfile(path):
        return default
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_text(path, text):
    _ensure_parent(path)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def save_json(path, data, indent=1):
    write_text(path, json.dumps(data, ensure_ascii=False, indent=indent))


def save_items(path, items):
    """JSON list with one item per line: readable for the agent without the cost of indentation."""
    write_text(path, "[\n" + ",\n".join(json.dumps(i, ensure_ascii=False) for i in items) + "\n]\n")


def append_jsonl(path, record):
    _ensure_parent(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path):
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def _ensure_parent(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
