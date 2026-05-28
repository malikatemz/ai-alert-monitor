"""
monitor.py - AI-powered monitoring and alerting system.
Usage: python monitor.py --config monitors.yaml
"""
import argparse, os, time, hashlib, requests, yaml
import anthropic
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL", "")

def ai_context(change_description: str) -> str:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return change_description
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content":
            f"In 2 sentences, explain why this monitoring alert matters and what to check first: {change_description}"}],
    )
    return msg.content[0].text.strip()

def send_slack(message: str, monitor_name: str):
    if not SLACK_WEBHOOK:
        print(f"  [ALERT] {monitor_name}: {message}")
        return
    requests.post(SLACK_WEBHOOK, json={
        "text": f":bell: *{monitor_name}*\n{message}"
    }, timeout=10)

def check_url(target: str, last_hash: str) -> tuple[str, str | None]:
    try:
        r = requests.get(target, timeout=10)
        content_hash = hashlib.md5(r.text.encode()).hexdigest()
        if last_hash and content_hash != last_hash:
            return content_hash, f"Content changed (status {r.status_code})"
        if r.status_code >= 400:
            return content_hash, f"HTTP {r.status_code} error"
        return content_hash, None
    except Exception as e:
        return last_hash or "", f"Request failed: {e}"

def check_file(target: str, last_hash: str, pattern: str | None = None) -> tuple[str, str | None]:
    try:
        content = open(target).read()
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if pattern and pattern in content:
            return content_hash, f"Pattern '{pattern}' found in {target}"
        if last_hash and content_hash != last_hash:
            return content_hash, f"File changed: {target}"
        return content_hash, None
    except Exception as e:
        return last_hash or "", f"File error: {e}"

def run_monitors(config_path: str):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    monitors = config.get("monitors", [])
    state = {m["name"]: {"hash": "", "last_check": 0} for m in monitors}
    print(f"[*] Monitoring {len(monitors)} targets. Ctrl+C to stop.\n")
    while True:
        now = time.time()
        for m in monitors:
            name = m["name"]
            interval = m.get("interval_seconds", 60)
            if now - state[name]["last_check"] < interval:
                continue
            state[name]["last_check"] = now
            mtype = m.get("type", "url")
            last = state[name]["hash"]
            if mtype == "url":
                new_hash, alert = check_url(m["target"], last)
            elif mtype == "file":
                new_hash, alert = check_file(m["target"], last, m.get("pattern"))
            else:
                continue
            state[name]["hash"] = new_hash
            if alert:
                context = ai_context(f"{name}: {alert}")
                send_slack(f"{alert}\n\n_{context}_", name)
                print(f"[{datetime.now():%H:%M:%S}] ALERT — {name}: {alert}")
            else:
                print(f"[{datetime.now():%H:%M:%S}] OK — {name}")
        time.sleep(5)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="monitors.yaml")
    args = p.parse_args()
    run_monitors(args.config)
