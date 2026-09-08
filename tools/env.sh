# Source this file from bash: source tools/env.sh
CANDI_PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export CANDI_TOOLS_ROOT="${CANDI_TOOLS_ROOT:-$HOME/.local/share/candi-tools}"
export PATH="$CANDI_PROJECT_ROOT/.venv/bin:$CANDI_TOOLS_ROOT/bin:$PATH"
unset CANDI_PROJECT_ROOT
