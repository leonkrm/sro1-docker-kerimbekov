"""Medeu Ice: строит отчёт out/report.json из файла data/records.csv."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
 
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "records.csv"
OUT = ROOT / "out" / "report.json"
VARIANT = 2
 
 
def load_rows():
    with open(DATA, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
 
 
def control_code(rows):
    text = "\n".join("|".join(row.values()) for row in rows)
    digest = hashlib.sha256(f"{VARIANT}\n{text}".encode("utf-8"))
    return digest.hexdigest()[:8].upper()
 
 
def money(value):
    return f"{value:,}".replace(",", " ") + " ₸"
 
 
CAPACITY = 120
 
 
def build(rows):
    by_session = defaultdict(int)
    by_ticket = defaultdict(lambda: [0, 0])
    for r in rows:
        qty, price = int(r["qty"]), int(r["price"])
        by_session[r["session"]] += qty
        t = by_ticket[r["ticket"]]
        t[0] += qty
        t[1] += qty * price
    total = sum(v[1] for v in by_ticket.values())
    sold = sum(by_session.values())
    summary = [
        {"label": "Общая выручка", "value": money(total)},
        {"label": "Продано билетов", "value": sold},
        {"label": "Средняя заполняемость", "value": f"{sold * 100 // (CAPACITY * len(by_session))}%"},
    ]
    sessions = sorted(by_session.items(), key=lambda kv: (-kv[1], kv[0]))
    tickets = sorted(by_ticket.items(), key=lambda kv: -kv[1][1])
    tables = [
        {"title": "Заполняемость сеансов",
         "columns": ["Сеанс", "Билетов", "Заполняемость"],
         "rows": [[k, v, f"{v * 100 // CAPACITY}%"] for k, v in sessions]},
        {"title": "Выручка по типам билетов",
         "columns": ["Тип билета", "Количество", "Выручка"],
         "rows": [[k, v[0], money(v[1])] for k, v in tickets]},
    ]
    return summary, tables
 
 
def main():
    rows = load_rows()
    summary, tables = build(rows)
    report = {
        "variant": VARIANT,
        "org": "Medeu Ice",
        "title": "Продажи сеансов на катке",
        "records": len(rows),
        "control_code": control_code(rows),
        "summary": summary,
        "tables": tables,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"out/report.json готов: {len(rows)} записей, контрольный код {report['control_code']}")
 
 
if __name__ == "__main__":
    main()
