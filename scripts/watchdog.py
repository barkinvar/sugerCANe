"""Monitor the authorized work session. Logs inactivity; never fabricates progress."""
from datetime import datetime, timezone
from pathlib import Path
import json
import time

root = Path(__file__).resolve().parents[1]
session = root / "reports/session"
deadline = datetime.fromisoformat(json.loads((session / "session.json").read_text())["deadline"])
last_state = None
while True:
    now = datetime.now(timezone.utc)
    heartbeat = json.loads((session / "heartbeat.json").read_text())
    age = (now - datetime.fromisoformat(heartbeat["at"])).total_seconds()
    remaining = (deadline - now).total_seconds()
    state = "deadline" if remaining <= 0 else "attention" if age > 300 else "active"
    record = {"at": now.isoformat(), "state": state, "heartbeat_age_s": round(age),
              "remaining_s": max(0, round(remaining)), "phase": heartbeat["phase"]}
    with (session / "watchdog.jsonl").open("a") as f:
        f.write(json.dumps(record) + "\n")
    (session / "watchdog-status.json").write_text(json.dumps(record, indent=2) + "\n")
    if state != last_state:
        print(json.dumps(record), flush=True)
        last_state = state
    if remaining <= 0:
        break
    time.sleep(min(30, remaining))
