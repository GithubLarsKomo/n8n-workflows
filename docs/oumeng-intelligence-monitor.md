# Oumeng Intelligence Monitor

Both Oumeng workflows are intentionally stored under `workflows/inactive/` because neither is currently active in n8n.

## v1
Direct monitor of the official Oumeng news page. It is preserved as a simple baseline/reference workflow. The previously exposed webhook secret is **not** stored here; mail uses `INTERNAL_MAIL_WEBHOOK_TOKEN`.

## v2
Discovery/evidence workflow: SearXNG → persistent MariaDB source lookup → Firecrawl capture → content-change detection → local Ollama evidence extraction → MariaDB evidence/event persistence → conservative materiality gate → internal mail.

The official Oumeng news page remains a primary-source seed. Search results are discovery leads, not evidence until captured. Secondary ownership/transaction/financing/management claims are marked for corroboration; recruiting/marketing signals do not prove ownership or closing.

### Before import/test
1. Run `sql/oumeng-intelligence-monitor-v2.sql` against the MariaDB database used for CI evidence.
2. Import the JSON from `workflows/inactive/`.
3. Select the existing MariaDB credential on both MySQL/MariaDB nodes (credential IDs are deliberately not committed).
4. Verify Docker DNS from n8n: `searxng:8080`, `firecrawl-api-1:3002`, and `ollama:11434`. The host-side Firecrawl endpoint may be `localhost:5030`; the workflow assumes n8n and Firecrawl share the Docker network.
5. Provide `INTERNAL_MAIL_WEBHOOK_TOKEN` to n8n or replace the header expression with an n8n credential. Never commit the token.
6. Keep the workflow inactive until a manual execution has been inspected.

### Gate
Default alert threshold: materiality ≥70 and confidence ≥75. A primary/official source can pass on its own. Secondary claims requiring corroboration remain silent in this first implementation until independently confirmed.

### Important
The v2 workflow uses HTTP calls to the local Ollama API rather than embedding a credential ID, keeping the export portable. The JSON is an implementation candidate and should be manually test-run in the target n8n 2.x instance before activation.
