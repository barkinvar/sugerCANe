# Source from bash. Prefer a release-local environment; allow the parent
# development environment without embedding its absolute path.
CANDI_REV_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export CANDI_TOOLS_ROOT="${CANDI_TOOLS_ROOT:-$HOME/.local/share/candi-tools}"
if [[ -d "$CANDI_REV_ROOT/.venv/bin" ]]; then
    export PATH="$CANDI_REV_ROOT/.venv/bin:$CANDI_TOOLS_ROOT/bin:$PATH"
elif [[ -d "$CANDI_REV_ROOT/../.venv/bin" ]]; then
    export PATH="$CANDI_REV_ROOT/../.venv/bin:$CANDI_TOOLS_ROOT/bin:$PATH"
else
    export PATH="$CANDI_TOOLS_ROOT/bin:$PATH"
fi
unset CANDI_REV_ROOT
