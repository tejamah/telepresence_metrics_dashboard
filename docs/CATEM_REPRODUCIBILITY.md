# CATEM Reproducibility Guide

This page is the reviewer-facing index for CATEM version 0.2.0. The included
records are deterministic software fixtures, not participant data.

## Materials

| Item | Location | What it contains |
|---|---|---|
| Dashboard screenshot | [`catem/dashboard_overview_full.png`](catem/dashboard_overview_full.png) | Current live-session, four-layer assessment, cross-cutting condition band, and object-drop event-window views |
| Sample CSV | [`../data/sample_metrics.csv`](../data/sample_metrics.csv) | Uploadable session records using the documented metric columns |
| Canonical event fixture | [`catem/catem_specification_v0.2.json`](catem/catem_specification_v0.2.json), key: `event_window_fixture` | Five ordered object-drop samples and their 35 traceable source records |
| Versioned CATEM specification | [`catem/catem_specification_v0.2.json`](catem/catem_specification_v0.2.json) | Four-layer schema, measurement-record schema, API response schema, transform registry, rule specifications, session fixtures, and the complete canonical object-drop event fixture |
| Verification results | [`catem/verification_results.json`](catem/verification_results.json) | Environment metadata and the 17 functional, reproducibility, and fault-injection checks reported by the software harness |
| Validation v1 method | [`CATEM_VALIDATION_V1.md`](CATEM_VALIDATION_V1.md) | Synthetic ground-truth timing, missingness, provenance, input-quality, export, and event-reconstruction method plus ESP32-S3 handoff |
| Validation v1 results | [`catem/validation_v1_results.json`](catem/validation_v1_results.json) and [`catem/validation_v1_results.csv`](catem/validation_v1_results.csv) | Machine-readable results from the separate 39-check deterministic validation harness |

The object-drop fixture is the `event_window_fixture` object inside the versioned
specification. It contains five ordered samples at offsets `-2`, `-1`, `0`,
`+1`, and `+2` seconds and 35 source records. The schema fields used to validate
that fixture are under `measurement_record_schema` and `api_response_schema` in
the same file.

## Run the implementation

From the repository root, start the API:

```bash
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8010
```

In a second terminal, start the dashboard:

```bash
cd apps/web
npm install
npm run dev
```

Open `http://127.0.0.1:5180`. The object-drop fixture is also available from
`GET http://127.0.0.1:8010/events/object-drop`.

## Re-run verification

```bash
cd apps/api
python verification.py
```

The command writes JSON and CSV outputs and exits with a nonzero status if any
check fails. To regenerate the versioned specification, run:

```bash
cd apps/api
python export_catem_specification.py
```

## Re-run Validation v1

The Validation v1 harness is intentionally separate from the original verifier:

```bash
cd apps/api
python validation_v1.py
```

The default run performs 100 deterministic replays and 100 three-source timing trials. Its synthetic quantitative timing results test the calculations against known inputs; they do not establish physical hardware accuracy. See [`CATEM_VALIDATION_V1.md`](CATEM_VALIDATION_V1.md) for the complete boundary and ESP32-S3 experiment handoff.
