import os
import time
import json
import requests
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------

H1_API_BASE = "https://api.hackerone.com/v1"
DASHBOARD_BASE = "https://security.ilevelace.com/api"

H1_TOKEN = os.getenv("H1_API_TOKEN")
OPERATOR = "LEVELACE_SENTINEL_ARCHITECT"

HEADERS_H1 = {
    "Authorization": f"Bearer {H1_TOKEN}",
    "Accept": "application/json",
    "User-Agent": f"HackerOne-{OPERATOR} (sentinel-pipeline)"
}

HEADERS_DASH = {
    "Content-Type": "application/json",
    "X-Operator": OPERATOR
}

# -------------------------
# PHASE 1 — HACKERONE SCOPE INGEST
# -------------------------

def fetch_h1_programs():
    url = f"{H1_API_BASE}/hacktivity"
    programs = []

    r = requests.get(url, headers=HEADERS_H1, timeout=30)
    r.raise_for_status()

    data = r.json()
    for item in data.get("data", []):
        program = item.get("relationships", {}).get("program", {}).get("data", {})
        if program:
            programs.append(program)

    return programs


def filter_web_only(programs):
    filtered = []

    for p in programs:
        attrs = p.get("attributes", {})
        scope = attrs.get("structured_scopes", [])

        web_scope = [
            s for s in scope
            if s.get("eligible_for_bounty")
            and s.get("asset_type") == "URL"
        ]

        if web_scope:
            filtered.append({
                "program": attrs.get("handle"),
                "scope": web_scope
            })

    return filtered


def push_scope_to_dashboard(scope_data):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "source": "HackerOne",
        "scope": scope_data
    }

    r = requests.post(
        f"{DASHBOARD_BASE}/scope/update",
        headers=HEADERS_DASH,
        data=json.dumps(payload),
        timeout=30
    )
    r.raise_for_status()


# -------------------------
# DASHBOARD CONTROL LOOP
# -------------------------

def wait_for_target_selection():
    while True:
        r = requests.get(
            f"{DASHBOARD_BASE}/target/next",
            headers=HEADERS_DASH,
            timeout=15
        )
        r.raise_for_status()
        data = r.json()

        if data.get("target"):
            return data

        time.sleep(10)


def update_phase_status(target, phase, status):
    payload = {
        "target": target,
        "phase": phase,
        "status": status,
        "time": datetime.utcnow().isoformat()
    }

    requests.post(
        f"{DASHBOARD_BASE}/phase/status",
        headers=HEADERS_DASH,
        data=json.dumps(payload),
        timeout=10
    )


# -------------------------
# PHASE EXECUTION STUBS
# -------------------------

def phase_2_recon(target):
    update_phase_status(target, "phase2", "running")
    time.sleep(5)  # placeholder
    update_phase_status(target, "phase2", "complete")


def phase_3_analysis(target):
    update_phase_status(target, "phase3", "running")
    time.sleep(5)
    update_phase_status(target, "phase3", "complete")


def phase_4_report(target):
    update_phase_status(target, "report", "assembling")
    time.sleep(3)
    update_phase_status(target, "report", "ready")


# -------------------------
# MAIN PIPELINE
# -------------------------

def main():
    if not H1_TOKEN:
        raise RuntimeError("H1_API_TOKEN not set")

    print("[+] Phase 1 — Fetching HackerOne scope")
    programs = fetch_h1_programs()
    web_scope = filter_web_only(programs)
    push_scope_to_dashboard(web_scope)

    print("[+] Scope published to dashboard")

    while True:
        print("[*] Awaiting operator target selection...")
        selection = wait_for_target_selection()

        target = selection["target"]
        phase = selection.get("phase", "phase2")

        print(f"[!] Operator triggered {phase} on {target}")

        if phase == "phase2":
            phase_2_recon(target)
            phase_3_analysis(target)
            phase_4_report(target)

        update_phase_status(target, "pipeline", "idle")


if __name__ == "__main__":
    main()
