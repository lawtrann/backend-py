#!/usr/bin/env python3
"""Post-write hook to create SQL files for Alembic migrations."""
import re
import sys
from pathlib import Path


def create_sql_files(revision_script: str) -> None:
    """Create upgrade and downgrade SQL files for a migration."""
    # Read the migration file to extract revision ID and message
    migration_file = Path(revision_script)
    content = migration_file.read_text()

    # Extract revision ID
    match = re.search(r"revision: str = ['\"]([^'\"]+)['\"]", content)
    if not match:
        print(f"Warning: Could not find revision ID in {revision_script}", file=sys.stderr)
        return

    revision_id = match.group(1)

    # Extract slug from filename (e.g., "20260213_0136_c9b3d9f23ffa_test_with_timestamp.py" -> "test_with_timestamp")
    # Handle both formats: {rev}_{slug}.py and {timestamp}_{rev}_{slug}.py
    filename_parts = migration_file.stem.split('_')
    # Find where the revision ID is and take everything after it
    try:
        rev_index = next(i for i, part in enumerate(filename_parts) if revision_id.startswith(part))
        slug = '_'.join(filename_parts[rev_index + 1:])
    except (StopIteration, IndexError):
        slug = "migration"

    # Extract revision message from docstring
    message_match = re.search(r'^"""(.+?)\n', content, re.MULTILINE)
    revision_message = message_match.group(1) if message_match else slug

    # Create SQL directory if it doesn't exist
    sql_dir = migration_file.parent.parent / "sql"
    sql_dir.mkdir(exist_ok=True)

    # Create upgrade SQL file with slug
    upgrade_file = sql_dir / f"{revision_id}_{slug}_upgrade.sql"
    upgrade_file.write_text(f"""-- {revision_message}
-- Revision: {revision_id}
-- Upgrade SQL

-- Add your upgrade SQL here

""")

    # Create downgrade SQL file with slug
    downgrade_file = sql_dir / f"{revision_id}_{slug}_downgrade.sql"
    downgrade_file.write_text(f"""-- {revision_message}
-- Revision: {revision_id}
-- Downgrade SQL

-- Add your downgrade SQL here

""")

    print("Created SQL files:")
    print(f"  - {upgrade_file}")
    print(f"  - {downgrade_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: create_sql_files.py <revision_script_path>", file=sys.stderr)
        sys.exit(1)

    create_sql_files(sys.argv[1])
