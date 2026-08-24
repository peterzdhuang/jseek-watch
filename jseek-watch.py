#!/usr/bin/env python3
"""Poll a public jseek.co watchlist and alert on new job postings.

Usage:
    python3 jseek-watch.py            # one poll; prints new jobs, updates state
    NTFY_TOPIC=mytopic python3 ...    # also push alerts to https://ntfy.sh/<topic>

Watch any public jseek.co watchlist (env vars):
    WATCHLIST_URL=https://jseek.co/en/owner/slug python3 jseek-watch.py
    STATE_FILE=my-state.json python3 jseek-watch.py   # optional custom state file
    A separate state file is auto-derived per watchlist URL, so multiple
    watchlists can run side by side without clobbering each other.

Email alerts (optional, via env vars):
    ALERT_TO=you@example.com SMTP_HOST=smtp.example.com SMTP_PORT=587 \
    SMTP_USER=you@example.com SMTP_PASS=secret python3 jseek-watch.py

    SMTP_TLS=starttls (default) or ssl for port 465.
    ALERT_FROM overrides the sender (defaults to SMTP_USER).

Run on a schedule (e.g. cron every 15 min):
    */15 * * * * cd /path/to/dir && /usr/bin/python3 jseek-watch.py >> /tmp/jseek-watch.log 2>&1
"""

import json
import os
import pathlib
import re
import smtplib
import sys
import urllib.request
from email.message import EmailMessage

DEFAULT_WATCHLIST_URL = "https://jseek.co/en/ph1425015107/new-watchlist"
WATCHLIST_URL = os.environ.get("WATCHLIST_URL") or DEFAULT_WATCHLIST_URL

if os.environ.get("STATE_FILE"):
    state_name = os.environ["STATE_FILE"]
elif WATCHLIST_URL == DEFAULT_WATCHLIST_URL:
    state_name = ".jseek-watchlist-state.json"
else:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", WATCHLIST_URL).strip("-")
    state_name = f".jseek-watchlist-state-{slug}.json"
STATE_FILE = pathlib.Path(__file__).with_name(state_name)

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"


def fetch_postings():
    req = urllib.request.Request(WATCHLIST_URL, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

    chunks = re.findall(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', html)
    if not chunks:
        raise SystemExit("no flight payload found (page structure changed?)")
    text = "".join(json.loads('"' + c + '"') for c in chunks)

    m = re.search(r'"postings":(\[.*?\]),"total":(\d+)', text)
    if not m:
        raise SystemExit("postings not found in payload (page structure changed?)")
    postings = json.loads(m.group(1))
    total = int(m.group(2))
    return postings, total


def send_ntfy(title, message, click=None):
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        return False
    url = topic if topic.startswith("http") else f"https://ntfy.sh/{topic}"
    req = urllib.request.Request(url, data=message.encode(), method="POST")
    req.add_header("Title", title)
    if click:
        req.add_header("Click", click)
    urllib.request.urlopen(req, timeout=15)
    return True


def send_email(title, message):
    to = os.environ.get("ALERT_TO")
    host = os.environ.get("SMTP_HOST")
    if not to or not host:
        return False
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASS", "")
    sender = os.environ.get("ALERT_FROM") or user or to

    msg = EmailMessage()
    msg["Subject"] = title
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(message)

    if os.environ.get("SMTP_TLS", "starttls") == "ssl":
        with smtplib.SMTP_SSL(host, port, timeout=15) as smtp:
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            smtp.starttls()
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
    return True


def send_alert(title, message, click=None):
    sent_ntfy = send_ntfy(title, message, click)
    sent_mail = send_email(title, message)
    if not sent_ntfy and not sent_mail:
        print(f"[alert] {title}\n{message}")


def main():
    postings, total = fetch_postings()
    now = {p["sourceUrl"]: p for p in postings if p.get("isActive")}

    state = {}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())

    known = set(state.get("known", []))
    new = [(url, p) for url, p in now.items() if url not in known]

    if new:
        lines = [
            f"- {p['title']} @ {p['company']['name']} ({', '.join(p.get('locationNames', []))})\n  {url}"
            for url, p in new
        ]
        send_alert(f"{len(new)} new job(s) on jseek watchlist", "\n".join(lines), click=new[0][0])
        for _, p in new:
            print(f"NEW: {p['title']} — {p['sourceUrl']}")

    json.dump({"known": sorted(now), "lastPolled": __import__("datetime").datetime.now().isoformat()},
              STATE_FILE.open("w"))
    print(f"checked {len(now)}/{total} postings, {len(new)} new")
    return 0


if __name__ == "__main__":
    sys.exit(main())
