# Google Drive Backup — Setup Guide

The `sync-to-drive.yml` workflow mirrors the entire GAIA-Core repository to a
Google Drive folder after every push to `main` and nightly at 03:00 UTC.

It is **completely read-only** with respect to this repository — it never
modifies source files or commits anything back.

---

## One-time setup (takes ~10 minutes)

### Step 1 — Create a Google Cloud project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. `gaia-drive-backup`)
3. Enable the **Google Drive API** for the project
   (`APIs & Services → Library → search "Drive" → Enable`)

### Step 2 — Create a Service Account
1. `IAM & Admin → Service Accounts → Create Service Account`
2. Name it `gaia-backup-agent` (or similar)
3. No special IAM roles needed at project level
4. Create a JSON key: `Keys → Add Key → JSON` — download the file

### Step 3 — Share your Drive folder
1. Create a folder in Google Drive (e.g. `GAIA-Core Backups`)
2. Right-click → Share → paste the service account email
   (looks like `gaia-backup-agent@your-project.iam.gserviceaccount.com`)
3. Give it **Editor** access
4. Copy the folder ID from the URL:
   `https://drive.google.com/drive/folders/<FOLDER_ID_IS_HERE>`

### Step 4 — Add GitHub Secrets
In this repository: `Settings → Secrets and variables → Actions → New repository secret`

| Secret name | Value |
|---|---|
| `GDRIVE_CREDENTIALS` | `base64 -w 0 your-key.json` output (the full base64 string) |
| `GDRIVE_FOLDER_ID` | The folder ID from Step 3 |

On macOS use: `base64 -i your-key.json | pbcopy`

### Step 5 — Verify
- Push any commit to `main` or go to `Actions → Backup to Google Drive → Run workflow`
- Check your Drive folder — a `GAIA-Core-backup-YYYY-MM-DD` folder should appear

---

## What gets backed up

Everything in the repo **except**:
- `.git/` (git internals)
- `__pycache__/`, `*.pyc`, `*.pyo`
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `.DS_Store`, `node_modules/`

---

## Backup folder naming

Each run creates or updates a folder named `GAIA-Core-backup-YYYY-MM-DD`
inside your target Drive folder. Multiple pushes on the same day update
the same dated folder (files are updated in place, not duplicated).

---

## Manual trigger

You can run a backup at any time:
`Actions → Backup to Google Drive → Run workflow → Run workflow`
