# jseek-watch

Gets a push notification on your phone whenever a **new job** appears on a [jseek.co](https://jseek.co) watchlist. Runs for free on GitHub Actions every 5 minutes.

## Setup (5 minutes)

**1. Fork or copy this repo to your own GitHub account.**

**2. Pick a topic name** — any random string, e.g. `my-jobs-9x7k2q`. This is your private notification channel.

**3. Add the topic as a secret** (so only your repo knows it):
- Go to your repo → **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret**
- Name: `NTFY_TOPIC`
- Value: your topic name
- Save

**4. Subscribe on your phone**:
- Install the **ntfy** app (Play Store / App Store)
- Open it, tap **+**, type your topic name, tap **Subscribe**
- Allow notifications

**5. Test it**:
- In your repo: **Actions** → **watch-jseek** → **Run workflow**
- Tick **"Send a test notification"** and run
- You should get a push within seconds. Done!

## Want to watch a different watchlist?

Go to **Settings → Secrets and variables → Actions → Variables** and add:

- Name: `WATCHLIST_URL`
- Value: any public watchlist URL, e.g. `https://jseek.co/en/colophongroup/maang`

Leave it empty to keep the default watchlist.

## Optional: also get an email copy

Add these secrets (same place as step 3): `ALERT_TO`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`.
