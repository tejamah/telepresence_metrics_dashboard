# Embodied Presence Internet Dashboard v3

## Reference

This document describes the current Embodied Presence Internet dashboard reference for CATEM v0.2.0. The corresponding 11-page rendering is preserved in [`embodied_presence_internet_dashboard_v3.pdf`](embodied_presence_internet_dashboard_v3.pdf).

## Included dashboard surface

The dashboard includes:

1. mission control and live synthetic telemetry;
2. four CATEM observational layers;
3. the separate cross-cutting Data and Interpretation Conditions band;
4. the canonical object-drop window with five offsets, seven measures, and 35 traceable records;
5. CATEM propositions and rule-based review prompts;
6. experimental future-work modules;
7. synthetic telemetry and heuristic prototype panels;
8. descriptive rule traces and hypothesis prompts;
9. core metrics and limited-sample analytics; and
10. the experimental research architecture and session comparison table.

The live simulator changes values over time, so regenerated dashboard PDFs may show different live values while preserving the same authored fixtures, layout, contracts, and interpretation boundaries.

## Scope boundary

The four CATEM layers, the separate \(D_t\) condition band, and the canonical event window are core CATEM v0.2.0 evidence views.

Later dashboard modules are experimental future-work prototypes. They should not be interpreted as validated predictive models, diagnostic tools, causal evidence, or production-ready capabilities.

The current terminology uses descriptive, rule-based wording. No event timing, probability, or predictive confidence is reported by the experimental risk-review modules.

The participant profile uses heuristic labels, fatigue is presented only as a prototype indicator, two-session relationships are qualified as candidate fixture patterns, and the final composite column is named `Prototype summary`.

## Reproduce

Start the API:

```bash
cd apps/api
python run_server.py
```

In a second terminal, start the dashboard:

```bash
cd apps/web
npm run dev
```

Open `http://127.0.0.1:5180`.

## Verification

The core CATEM v0.2.0 implementation retains the original 17-check software-verification result. Additional synthetic validation work is maintained separately on the `catem-validation-v1` branch, including the 39-check ground-truth suite and the 33-check end-to-end pipeline suite.
