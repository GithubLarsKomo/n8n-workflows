# n8n Workflow Inventory

Last reviewed: 2026-09-18.

## Verified active in the current operational session

| Workflow | Purpose | Status |
|---|---|---|
| FDA 510(k) / PMN watcher | FDA PMNLSTMN monitoring for selected companies and IVD product codes | Active/observed |
| EUDAMED UDI watcher | EUDAMED manufacturer/MF_SRN monitoring with normalized MariaDB upsert and change tracking | Active/observed |

## Completeness

This is not yet a complete runtime inventory. The authoritative complete list must be generated from the live n8n instance using scripts/export-active-workflows.py, which requests /api/v1/workflows?active=true and follows pagination.

The private durable documentation for architecture and lessons is in GithubLarsKomo/n8n-brain.
