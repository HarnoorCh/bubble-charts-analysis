---
name: reference_dashboards_hosting
description: "Self-contained HTML+Chart.js dashboard pattern; GCS bucket with Domain Restricted Sharing; ngrok quick-share"
metadata:
  type: reference
---

Dashboard / hosting patterns.

- **Pattern:** self-contained HTML + Chart.js — `bq query --format=json` via subprocess → embed data inline → offline, shareable single file (no server). Proven scripts: `talabat_jump_build.py`, `build_dashboard.py`. PDF export via headless Chrome (`--headless=new --print-to-pdf`).
- **GCS hosting:** bucket `gs://dh-cpl-seamless-dashboards` (project `logistics-data-storage-staging`). It has **Domain Restricted Sharing** org policy — blanket `domain:` grants are silently stripped; grant `user:<email>@deliveryhero.com` individually via `gcloud storage buckets add-iam-policy-binding <bucket> --member=user:<email> --role=roles/storage.objectViewer`. Browser URL = `storage.cloud.google.com/...` (Google-login-gated). Set up with `--uniform-bucket-level-access --public-access-prevention`.
- **Quick public share:** `python3 -m http.server 8000` in the folder + `ngrok http 8000`; get the URL from `curl -s http://localhost:4040/api/tunnels`. Free tier = ONE tunnel at a time (second fails ERR_NGROK_334). Exposes everything in the folder — make it self-contained first. Stop: `pkill -f "ngrok http"`. Related: [[project_talabat_jump_experiment]], [[project_country_ranking_hackathon]].
