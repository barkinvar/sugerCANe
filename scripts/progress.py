"""Record a real completed step or current design task for the watchdog/log."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys

root = Path(__file__).resolve().parents[1]
(root / "reports/session").mkdir(parents=True, exist_ok=True)
record = {"at": datetime.now(timezone.utc).isoformat(), "phase": " ".join(sys.argv[1:])}
(root / "reports/session/heartbeat.json").write_text(json.dumps(record, indent=2) + "\n")
with (root / "reports/session/work-log.jsonl").open("a") as f:
    f.write(json.dumps(record) + "\n")
print(record["phase"])
