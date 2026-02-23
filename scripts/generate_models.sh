#!/usr/bin/env bash
# Regenerate SQLModel models from the live database.
#
# Usage:
#   bash scripts/generate_models.sh
#   DATABASE_URL=postgresql://user:pass@host/db bash scripts/generate_models.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

DATABASE_URL="${DATABASE_URL:-postgresql://postgres:example@localhost:15432/backend}"
OUTFILE="$BACKEND_DIR/app/infra/db/models.py"

echo "Generating models from: $DATABASE_URL"
echo "Output: $OUTFILE"

uv run sqlacodegen --generator sqlmodels "$DATABASE_URL" --outfile "$OUTFILE"

echo "Done. Review $OUTFILE and adjust if needed."
