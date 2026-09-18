# n8n Workflows

Source control for n8n workflows.

This repository is public, therefore only sanitized workflow JSON belongs here. Never commit API keys, decrypted credentials, passwords, tokens, private headers, or secrets.

## Layout

- workflows/active/ — sanitized exports of workflows that are active/published in the live n8n instance.
- docs/WORKFLOW-INVENTORY.md — human-readable inventory.
- scripts/export-active-workflows.py — live exporter using the n8n Public API.
- scripts/sync-active-workflows.sh — convenience wrapper to export, inventory, commit and optionally push.

## Required environment

    export N8N_BASE_URL="https://your-n8n.example.com"
    export N8N_API_KEY="..."

The API key is read only from the environment and must never be committed.

## Export

    python3 scripts/export-active-workflows.py

The exporter requests only active workflows, follows n8n pagination, removes credential bindings and common secret-bearing fields, and writes deterministic JSON files.

Review the diff before pushing because workflow parameters can contain arbitrary user-authored text.

## Sync

    bash scripts/sync-active-workflows.sh

To push after review:

    PUSH=1 bash scripts/sync-active-workflows.sh

## Restore

These public exports are intentionally sanitized and require credential reassignment after import. They are source-control artifacts, not decrypted disaster-recovery backups.
