#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

from decimal import Decimal

# Latest attempt per txn_id (by ts; ISO-8601 UTC strings sort chronologically).
latest = {}

with open(os.path.join(HERE, "payments.jsonl"), encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict) or not event.get("txn_id"):
            continue
        txn = event["txn_id"]
        if txn not in latest or event["ts"] >= latest[txn]["ts"]:
            latest[txn] = event

total = Decimal(0)
count = 0
for event in latest.values():
    if event["status"] == "success":
        # amounts may be numbers or strings like "12,345.67"
        total += Decimal(str(event["amount"]).replace(",", ""))
        count += 1

with open(os.path.join(HERE, "expected.txt")) as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
