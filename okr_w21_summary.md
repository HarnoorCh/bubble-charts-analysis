# Seamless OKR Summary — Week 21 (Q2 2026)

## O3: Building customer trust through reliable delivery promises ( @Uri Alarcon )

- **KR — Increase incremental annualized GMV from 12.9 m€ to 63.0 m€ via improved DTEs ( @Harnoor Chahal ) — W21: 40.5 m€ ⚠️ AT RISK**
  - No rollouts since last week — speed has slowed
  - New this week:
    - TW narrow aggressive ranges rolled out → 5.3 M€ GMV ([wiki](https://atlassian.cloud.deliveryhero.group/wiki/x/hIH-T))
    - NO narrow aggressive ranges rolled out → 4.4 M€ GMV ([wiki](https://atlassian.cloud.deliveryhero.group/wiki/x/AYCxSQ))
  - Older: Q1 Glovo PDT ranges rolled out for all countries except IT → 8.9 M€ GMV ([wiki](https://atlassian.cloud.deliveryhero.group/wiki/x/DYCZQ)); Spain rollout the week before → 9 M€ GMV
  - **Initiatives:**
    - **Run 20 A/B tests on PDT ranges ( @Hirbod Kamalinia ) — W21: 13 🟢 ON-TRACK**
      - 12 Manual PDT range tests ongoing: 5 PeYa (AR/CR/NI/VE/PE), 2 surge (BD/PK), 3 vertical-level reliability (QA/JO/OM), 1 aggressive lower/narrower MY, 1 Pandora HU aggressive
      - Model-based ranges: 1 started (Pandora HK); 11 in discussion (4 TB + 5 PY + SA + SG)
      - DS: streamlining range generation; Phase II — stacking probability concluded as condition variable, results next week
    - **Run 2 A/B tests on Neural Networks for PDTs ( @Sudhanshu Nautiyal ) — W21: 0 ⚠️ AT RISK**
      - Different countries behaving very differently on on-time performance; investigating root cause
    - **Run 3 A/B tests on format-agnostic "Jump Stations" for ETA ( @Anderson Engroff ) — W21: 1 🟢 ON-TRACK**
      - GV started
      - TB stopped due to metric degradation

- **KR — Improve PET by 3.0 ppt through better EPT ( @Ege Sözgen ) — W21: 1.44% ⚠️ AT RISK**
  - Improvement only half-way; expecting decline with Eid next week
  - Gains from prep-time feature improvements only realized end of Q
  - Quantile test rollouts this/next week need redo after new prep-time features
  - **Initiatives:**
    - **2 switchback tests adding live features to restaurant preptime model ( @Kaushik Pandurang Gaikwad ) — W21: 0 🟢 ON-TRACK**
      - Request/response testing done on small EU sample
      - Switchback smoke test in DE2 (+ small countries per region) to validate prod
      - Full deploy planned by Wed/Thu
    - **2 switchback tests to improve PET for Shops vertical ( @Kaushik Pandurang Gaikwad ) — W21: 0 🟢 ON-TRACK**
      - Bundled with the test above
    - **Run 3 preptime configuration experiments that improve PET ( @Ege Sözgen ) — W21: 3 🟢 ON-TRACK**
      - Rolled out improved quantiles in PeYa (1.2%), Talabat (0.3%), Pandora (1.2%) last week

- **KR — Run 4 A/B tests on OT SDK proving better CX ( @Tomás Ignacio Perticari ) — W21: 1 🚨 OFF-TRACK**
  - Done: Map v1 concluded & rolled out at Glovo ([DXI audit](https://dxi-audit.vercel.app/?share=8e591e52-6294-45d5-8d48-8f5ccbaf633b))
  - In progress: Map v2 integration/test/rollout at PeYa and efood
  - Next: Map v2 test at HungerStation (planned mid-June)
  - Blocked: Map v2 test at Glovo — delays at HS/GV due to deprioritization vs v1→v2 bump (potentially escalating)
  - **Initiatives:**
    - **Integrate, test, roll out Map v2 at PeYa & efood ( @Harsha Kundilepath ) — W21: 0 ⚠️ AT RISK**
      - In progress: PY (iOS + Android) and EF (iOS + Android) integrations
      - Next: PY and EF experiments → rollouts
    - **Run 2 A/B tests with Map v2 vs v1 at HS & GV ( @Shradha Jain ) — W21: 0 🚨 OFF-TRACK**
      - Next: Map v2 integration upgrade in HS (early June)
      - Not started: HS experiment
      - Blocked: GV integration upgrade + experiment
    - **Ship Order Status Component for Q3 2026 A/B tests ( @Harsha Kundilepath ) — W21: 2 ⚠️ AT RISK**
      - Done: PRD approved, Tech Analysis concluded
      - In progress: Designs handoff, Time Estimation (different ETA formats)
      - Not started: Order Status support, Late handling, Edge cases (split / stacked), Flow customisation (verticals), new TSDK API interface, QA

## Cross-cutting / Foundation initiatives (not under a specific KR)

- **Ship weather signal on control areas (KMA / Accuweather minute cast) ( @Uri Alarcon ) — W21: 0 ⚠️ AT RISK**
  - PRD closed; RFC for M1 in progress; RFC for M2 not started
  - M1 planned mid-June; M2 end-of-June (more risk — RFC not started)

- **The recorder and replayer for playing past recorded sessions (TUI) ( @Harsha Kundilepath ) — W21: — 🟢 ON-TRACK** *(carried from W20; no W21 note)*

- **Upgrade ldsutils to MLPkit in preptime (SDS) ( @Sudhanshu Nautiyal ) — W21: 0 🟢 ON-TRACK**
  - Plan to complete in 1.5 weeks
  - Phase 1/5 implemented & validated; Phases 2 & 3/5 in implementation

- **Enable more granular PDT configuration flexibility (TES) ( @Mahmood Nasir ) — W21: 0 🟢 ON-TRACK**
  - Refinement complete, tasks created, in sprint for generation & review

- **Notification Service to listen to ETA Upper Bound for Countdown format (OTX) ( @Anderson Engroff ) — W21: 0 🟢 ON-TRACK**
  - Herogen work done; currently in QA

- **Make experiments and model changes safe for production (load testing + SLA) ( @Pranav Jariwala ) — W21: 2 🟢 ON-TRACK**
  - Done: Load test TAPI-TTM, Load test CNS (KT, handover, AI docs, teams executing)
  - In progress (expected next week): Load test TES-DTM, Load test TES-Prep Time
  - To do: SLA benchmarking
