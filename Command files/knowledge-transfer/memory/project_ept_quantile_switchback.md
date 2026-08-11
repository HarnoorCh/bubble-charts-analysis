---
name: project_ept_quantile_switchback
description: "EPT quantile switchback test process (Ege's steps): find current quantile (Superset 480 + operational_config.yaml), change via PR, OOO routing"
metadata:
  type: project
---

**EPT quantile switchback tests** — process from **Ege Sözgen** (Product Ops) in `#cpl-sds-int` (C08P93C21FE, private).

- **Find current quantile:** Superset dashboard 480 (https://superset.syslogistics.io/superset/dashboard/480/, main submodel = restaurants) and Git `operational_config.yaml` in **deliveryhero/logistics-preptimes** (`preptimes/operational_config.yaml`, branch master/model-b).
- **Change it:** edit that YAML via a PR (GitHub web pencil → "Create a new branch" e.g. `w27-pandora-quantile-changes`, or `gh repo clone deliveryhero/logistics-preptimes`).
- **While Ege OOO route through:** Hirbod Kamalinia (`U023ZA36ATT`, PR review/merge + training), Alper Duranel (`U08QHH5Q8V8`, training/deploy), Sudhanshu Nautiyal (`UJHSR4E8H`, model/test setup), Kaushik P Gaikwad (`U03N17AB220`, Airflow training DAG), Alina Kim (`U09D065SRT6`, design-doc/query). Related: [[reference_people_channels]].
