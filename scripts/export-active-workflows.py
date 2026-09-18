#!/usr/bin/env python3
"""Export all active n8n workflows as sanitized deterministic JSON.

Configuration:
  The script loads .env from the repository root (one directory above scripts/)
  when present. Already exported environment variables take precedence.

  N8N_BASE_URL       Base URL of the n8n instance, without /api/v1.
  N8N_API_KEY        n8n Public API key.
  N8N_BYPASS_PROXY   Set to true for an internal n8n host that must not use
                     HTTP(S)_PROXY. Defaults to false.

The repository is public. This script removes credential bindings and common
secret-bearing values, but workflow parameters are arbitrary user content.
Always review the git diff before pushing.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"
OUT_DIR = REPO_ROOT / "workflows" / "active"
INVENTORY = REPO_ROOT / "docs" / "WORKFLOW-INVENTORY.generated.md"


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE pairs without overwriting the process environment."""
    if not path.is_file():
        return

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(),
        start=1,
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[7:].lstrip()

        if "=" not in line:
            die(f"{path}:{line_number}: expected KEY=VALUE.")

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            die(f"{path}:{line_number}: invalid environment variable name {key!r}.")

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        else:
            # Allow comments after unquoted values when separated by whitespace.
            value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()

        os.environ.setdefault(key, value)


load_env_file(ENV_FILE)

BASE_URL = os.environ.get("N8N_BASE_URL", "").rstrip("/")
API_KEY = os.environ.get("N8N_API_KEY", "")
BYPASS_PROXY = os.environ.get("N8N_BYPASS_PROXY", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

HTTP_OPENER = urllib.request.build_opener(
    urllib.request.ProxyHandler({}) if BYPASS_PROXY else urllib.request.ProxyHandler()
)

SECRET_KEY_RE = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|authorization|private[_-]?key|"
    r"client[_-]?secret|access[_-]?key|bearer|credential)",
    re.IGNORECASE,
)
SECRET_HEADER_RE = re.compile(
    r"^(authorization|proxy-authorization|x-api-key|api-key|x-auth-token)$",
    re.IGNORECASE,
)


def request_json(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "accept": "application/json",
            "X-N8N-API-KEY": API_KEY,
        },
    )

    retryable_statuses = {429, 502, 503, 504}
    max_attempts = 4

    for attempt in range(1, max_attempts + 1):
        try:
            with HTTP_OPENER.open(req, timeout=60) as response:
                return json.load(response)

        except urllib.error.HTTPError as exc:
            body = exc.read(2048).decode("utf-8", errors="replace").strip()
            retryable = exc.code in retryable_statuses and attempt < max_attempts

            if retryable:
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = max(1, int(retry_after)) if retry_after else 2 ** (attempt - 1)
                except ValueError:
                    delay = 2 ** (attempt - 1)

                print(
                    f"n8n API returned HTTP {exc.code}; "
                    f"retrying in {delay}s ({attempt}/{max_attempts})...",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue

            detail = f"\nResponse body: {body}" if body else ""
            proxy_hint = (
                "\nProxy bypass is OFF. If this is an internal n8n host behind "
                "a corporate proxy, set N8N_BYPASS_PROXY=true in the root .env."
                if not BYPASS_PROXY
                else "\nProxy bypass is ON."
            )
            die(
                f"n8n API request failed: HTTP {exc.code} {exc.reason}\n"
                f"URL: {url}{detail}{proxy_hint}"
            )

        except urllib.error.URLError as exc:
            proxy_hint = (
                "\nProxy bypass is OFF. If this is an internal n8n host behind "
                "a corporate proxy, set N8N_BYPASS_PROXY=true in the root .env."
                if not BYPASS_PROXY
                else "\nProxy bypass is ON."
            )
            die(f"n8n API connection failed: {exc.reason}\nURL: {url}{proxy_hint}")

    die("n8n API request failed after retries.")


def sanitize_url(value: str) -> str:
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        return value
    if not parsed.scheme or not parsed.netloc or "@" not in parsed.netloc:
        return value
    host = parsed.netloc.split("@", 1)[1]
    return urllib.parse.urlunsplit(
        (parsed.scheme, host, parsed.path, parsed.query, parsed.fragment)
    )


def sanitize(value, parent_key=None):
    if isinstance(value, dict):
        if parent_key == "credentials":
            return {"__redacted__": "credential bindings removed"}

        header_name = value.get("name")
        if isinstance(header_name, str) and SECRET_HEADER_RE.match(header_name.strip()):
            copied = dict(value)
            if "value" in copied:
                copied["value"] = "__REDACTED__"
            return {key: sanitize(item, key) for key, item in copied.items()}

        result = {}
        for key, item in value.items():
            if key in {"pinData", "staticData", "shared", "homeProject", "meta"}:
                continue
            if SECRET_KEY_RE.search(str(key)):
                result[key] = "__REDACTED__"
            else:
                result[key] = sanitize(item, str(key))
        return result

    if isinstance(value, list):
        return [sanitize(item, parent_key) for item in value]

    if isinstance(value, str):
        if value.startswith(("http://", "https://")):
            return sanitize_url(value)
        return value

    return value


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", name.strip()).strip("-").lower()
    return slug or "workflow"


def fetch_active_workflows():
    workflows = []
    cursor = None

    while True:
        params = {
            "active": "true",
            "limit": "250",
            "excludePinnedData": "true",
        }
        if cursor:
            params["cursor"] = cursor

        url = f"{BASE_URL}/api/v1/workflows?{urllib.parse.urlencode(params)}"
        payload = request_json(url)

        if isinstance(payload, list):
            page = payload
            cursor = None
        else:
            page = payload.get("data", [])
            cursor = payload.get("nextCursor")

        if not isinstance(page, list):
            die("Unexpected n8n workflow-list response shape.")

        workflows.extend(page)

        if not cursor:
            break

    return workflows


def write_exports(workflows):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    expected = set()
    inventory_rows = []

    for workflow in workflows:
        workflow_id = str(workflow.get("id", "unknown"))
        name = str(workflow.get("name", "Unnamed workflow"))
        filename = f"{slugify(name)}--{workflow_id}.json"
        path = OUT_DIR / filename
        expected.add(path.resolve())

        clean = sanitize(workflow)
        path.write_text(
            json.dumps(clean, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        nodes = workflow.get("nodes") or []
        trigger_types = sorted(
            {
                str(node.get("type", ""))
                for node in nodes
                if "trigger" in str(node.get("type", "")).lower()
            }
        )
        inventory_rows.append(
            (
                name,
                workflow_id,
                ", ".join(trigger_types) if trigger_types else "—",
                len(nodes),
            )
        )

    for old in OUT_DIR.glob("*.json"):
        if old.resolve() not in expected:
            old.unlink()

    inventory_rows.sort(key=lambda row: row[0].lower())

    lines = [
        "# Generated Active n8n Workflow Inventory",
        "",
        "Generated from the live n8n Public API with active=true.",
        "",
        "| Workflow | ID | Trigger node types | Nodes |",
        "|---|---|---|---:|",
    ]

    for name, workflow_id, trigger_types, node_count in inventory_rows:
        safe_name = name.replace("|", "\\|")
        safe_triggers = trigger_types.replace("|", "\\|")
        lines.append(
            f"| {safe_name} | {workflow_id} | {safe_triggers} | {node_count} |"
        )

    lines += ["", f"Total active workflows: {len(inventory_rows)}.", ""]
    INVENTORY.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not BASE_URL:
        die("N8N_BASE_URL is not set.")
    if BASE_URL.endswith("/api/v1"):
        die("N8N_BASE_URL must not include /api/v1.")
    if not API_KEY:
        die("N8N_API_KEY is not set.")

    print(
        f"Using n8n instance {BASE_URL} "
        f"(proxy bypass {'on' if BYPASS_PROXY else 'off'})."
    )

    workflows = fetch_active_workflows()
    write_exports(workflows)
    print(f"Exported {len(workflows)} active workflow(s) to {OUT_DIR}/")


if __name__ == "__main__":
    main()
