"""Export the pending bench procedures as a fillable spreadsheet; no measurements."""
from pathlib import Path
import csv

root = Path(__file__).resolve().parents[1]
rows = []
for line in (root/'docs/BRING_UP.md').read_text().splitlines():
    if not line.startswith('|'):
        continue
    cells = [c.strip() for c in line.strip('|').split('|')]
    if len(cells) != 3 or cells[0] == 'Stage' or set(cells[0]) <= {'-', ' '}:
        continue
    rows.append(cells)
assert len(rows) >= 25
with (root/'reports/bench_test_plan.csv').open('w',newline='') as f:
    writer=csv.writer(f)
    writer.writerow(['test_id','stage','procedure','initial_acceptance_target',
                     'status','actual_result','evidence_file','board_serial',
                     'firmware_sha256','date','tester'])
    for i,row in enumerate(rows,1):
        writer.writerow([f'B{i:02d}',*row,'PENDING','','','','','',''])
print(f'Exported {len(rows)} pending bench stages; no actual measurements entered.')
