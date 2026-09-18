#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 scripts/export-active-workflows.py

git add workflows/active docs/WORKFLOW-INVENTORY.generated.md

if git diff --cached --quiet; then
  echo "No active workflow changes."
  exit 0
fi

echo
echo "Staged changes:"
git diff --cached --stat
echo
echo "IMPORTANT: this repository is public."
echo "Review the full staged diff for secrets before pushing:"
echo "  git diff --cached"
echo

git commit -m "Sync active n8n workflows"

if [[ "${PUSH:-0}" == "1" ]]; then
  git push
else
  echo "Commit created locally. Run git push after review, or rerun with PUSH=1."
fi
