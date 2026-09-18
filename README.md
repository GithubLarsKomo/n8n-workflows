# n8n Workflows

Source control for n8n workflows.

This repository is public, therefore only sanitized workflow JSON belongs here. Never commit API keys, decrypted credentials, passwords, tokens, private headers, or secrets.

## Layout

- workflows/active/ — sanitized exports of active/published workflows.
- workflows/inactive/ — sanitized exports of inactive workflows.
- docs/WORKFLOW-INVENTORY.md — human-readable inventory.
- scripts/export-active-workflows.py — live exporter for active and inactive workflows using the n8n Public API.
- scripts/sync-active-workflows.sh — convenience wrapper to export, inventory, commit and optionally push.

## Configuration

The exporter automatically loads `.env` from the repository root:

    cp .env.example .env

Example:

    N8N_BASE_URL=https://your-n8n.example.com
    N8N_API_KEY=...
    N8N_BYPASS_PROXY=false

You may also export the variables in the shell:

    export N8N_BASE_URL="https://your-n8n.example.com"
    export N8N_API_KEY="..."

Already exported environment variables take precedence over values from `.env`.

For an internal n8n host that must not use a corporate `HTTP_PROXY`/`HTTPS_PROXY`, set:

    N8N_BYPASS_PROXY=true

This bypass applies only to this exporter process. If `N8N_BYPASS_PROXY` is false, Python's normal proxy and `NO_PROXY` handling remains in effect.

The exporter retries HTTP 429/502/503/504 responses and prints a concise response body plus a proxy hint when the request still fails.

The repository is public. `.env` and `.env.*` are ignored by Git; `.env.example` is the only exception. Never commit the real API key.

## Export

    python3 scripts/export-active-workflows.py

The exporter queries both `active=true` and `active=false`, follows n8n API pagination for each set, removes credential bindings and common secret-bearing fields, and writes deterministic JSON files into separate `workflows/active/` and `workflows/inactive/` directories. Files that no longer belong to a status are removed from that directory on the next export.

Review the diff before pushing because workflow parameters can contain arbitrary user-authored text.

## Sync

    bash scripts/sync-active-workflows.sh

To push after review:

    PUSH=1 bash scripts/sync-active-workflows.sh

## Restore

These public exports are intentionally sanitized and require credential reassignment after import. They are source-control artifacts, not decrypted disaster-recovery backups.
