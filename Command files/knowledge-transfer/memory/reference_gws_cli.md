---
name: reference_gws_cli
description: "Google Workspace via gws CLI: read/write Sheets, upload CSV as native Sheet, read Slides, and the auth-token refresh block"
metadata:
  type: reference
---

`gws` CLI (skill at `~/.claude/skills/google-workspace`), backed by gcloud application-default credentials.

- Read sheet: `gws sheets +read --spreadsheet <id> --range "<tab>" --format table`. List tabs: `gws sheets spreadsheets get --params '{"spreadsheetId":"<id>"}'`.
- Write: `gws sheets spreadsheets values update --params '{"spreadsheetId":"<id>","range":"<tab>!A1","valueInputOption":"RAW"}' --json '{"values":[...]}'`. Add/rename tabs via `batchUpdate` (`addSheet`/`updateSheetProperties`).
- Upload CSV as a native Sheet: `gws drive files create --upload file.csv --upload-content-type text/csv --json '{"name":"...","mimeType":"application/vnd.google-apps.spreadsheet"}'` (upload from cwd, not /tmp).
- Read slides: `gws slides presentations get --params '{"presentationId":"<id>"}'` (large — extract text only). `batchUpdate` needs `presentationId` in `--params`, body in `--json`; scope `replaceAllText` with `pageObjectIds`.
- Filter `keyring` noise: `... | grep -v keyring`.
- **Auth refresh** when it fails:
```bash
export GCLOUD_SDK_ROOT=$(gcloud info --format="value(installation.sdk_root)")
export PYTHONPATH="$GCLOUD_SDK_ROOT/lib/third_party:$GCLOUD_SDK_ROOT/lib"
export GOOGLE_WORKSPACE_CLI_TOKEN=$(python3 -c "import google.auth; from google.auth.transport.requests import Request; creds,_=google.auth.default(scopes=['https://www.googleapis.com/auth/spreadsheets']); creds.refresh(Request()); print(creds.token)")
```
Gmail+Calendar need `gcloud auth application-default login --scopes=openid,userinfo.email,cloud-platform,drive,spreadsheets,documents,presentations,calendar,gmail.compose,gmail.send,gmail.readonly`. Tokens expire ~daily.
