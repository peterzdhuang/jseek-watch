# jseek-watch

Polls a public [jseek.co](https://jseek.co) watchlist every 5 minutes via GitHub Actions and sends a push notification when new job postings appear.

## Setup

1. Pick a private topic name for [ntfy.sh](https://ntfy.sh) (e.g. `jseek-alerts-<random>`).
2. Add it as a repo secret: **Settings → Secrets and variables → Actions → New repository secret**, name `NTFY_TOPIC`.
3. Install the [ntfy app](https://ntfy.sh) on your phone (or open `https://ntfy.sh/<topic>` in a browser) and subscribe to the topic.
4. Test: **Actions → watch-jseek → Run workflow**, then send a test push: `curl -d "test" https://ntfy.sh/<topic>`.

Optional email alerts: add secrets `ALERT_TO`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` (see header of `jseek-watch.py`).
