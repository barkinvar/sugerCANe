#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source tools/env.sh
python scripts/build_architecture_diagram.py
python scripts/build_wiring_card.py
python scripts/build_bom_pdf.py
python scripts/build_bench_plan.py
python scripts/render_crystal_lands.py
python scripts/build_handbook.py
python scripts/build_source_manifest.py
python scripts/check_document_links.py
python scripts/verify_documentation.py
