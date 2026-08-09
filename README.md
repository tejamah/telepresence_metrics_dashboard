# Embodied Presence Internet

## CATEM — A Timestamp-Aware Cross-Layer Framework for Telepresence Evaluation

The **Embodied Presence Internet** is a research platform for Human-Robot Interaction (HRI), telepresence, VR/AR, robotics, embodied AI, and multimodal human-experience research.

The current research implementation centers on **CATEM: A Timestamp-Aware Cross-Layer Framework for Telepresence Evaluation**, an open-source measurement and reporting framework for organizing heterogeneous telepresence evidence around shared task events.

CATEM reproducibility materials are indexed in the [CATEM Reproducibility Guide](docs/CATEM_REPRODUCIBILITY.md), with direct links to the canonical object-drop fixture, versioned specification, verification results, sample data, and dashboard screenshot.

The current release focuses on measurement organization, timestamp-aware alignment, provenance, missingness, transformation traceability, event-centered inspection, and reproducible software verification.

The broader **Embodied Presence Internet** vision is described separately under **Future Research**. Those roadmap items are not claims about implemented or scientifically validated CATEM v0.2.0 capabilities.

---

## Research Motivation

Telepresence studies often combine robot telemetry, network measurements, tracking, behavioral observations, workload measures, physiological measurements, and subjective experience measures.

These streams may differ in units, sampling rates, timestamps, missingness, provenance, and interpretation. CATEM provides a common measurement contract for preserving these distinctions while allowing researchers to inspect measurements around shared task events.

CATEM supports evidence organization and reporting. It does **not** collapse heterogeneous constructs into a universal telepresence score.

---

## CATEM v0.2.0 — Implemented Scope

The current research prototype supports:

- CSV-based stored-session ingestion
- FastAPI REST interfaces
- WebSocket telemetry ingestion
- Timestamp-aware event alignment
- Event-centered evidence inspection
- Explicit missing-data representation
- Provenance tracking
- Transformation traceability
- Measurement and response schemas
- Dashboard visualization
- JSON and CSV research artifacts
- Canonical object-drop event fixture
- Controlled fault-injection verification
- Deterministic replay
- Versioned reproducibility artifacts

---

## CATEM Evidence Model

CATEM organizes evidence into four observational layers:

1. **Experience** — agency, ownership, self-location, presence, social presence
2. **Action** — task error, task efficiency, completion time, path efficiency, safety events
3. **Human State and Cognition** — workload, heart rate, HRV, galvanic response, cybersickness, situation awareness
4. **System** — latency, jitter, frame rate, packet loss, tracking dropout, haptic delay

These layers organize observations without asserting that measures in different layers are interchangeable.

### Data and Interpretation Conditions

CATEM separately records cross-cutting **Data and Interpretation Conditions**, including:

- timestamp-alignment quality
- missingness
- provenance
- preprocessing
- transformation history
- reliability evidence
- interpretation boundaries

These conditions qualify evidence across the four observational layers and are **not a fifth layer**.

---

## Measurement Contract

CATEM uses an executable measurement contract to describe how evidence should be represented and preserved.

A measurement record can retain:

- participant or session identifier
- task identifier
- metric identifier
- construct identifier
- observational layer
- raw value
- unit
- timestamp
- sensor or instrument
- sampling information
- missingness state
- provenance
- preprocessing information
- transformation version
- interpretation boundary

Expected-but-absent measurements remain explicit rather than silently disappearing.

---

## Event-Centered Analysis

The canonical software-verification fixture uses an object-drop event at `t = 0` with five explicit samples:

```text
-2 s
-1 s
 0 s
+1 s
+2 s
```

Seven measures are represented across the window:

- latency
- packet loss
- tracking dropout
- workload
- heart rate
- agency
- task error

This yields **35 traceable source records**.

Temporal alignment indicates co-occurrence inside the selected evidence window. It does **not** establish causality.

---

## Synthetic Verification Data

The current CATEM verification uses **authored synthetic data** designed to exercise the software pipeline under deterministic and repeatable conditions.

The current verification data are not:

- participant-derived measurements
- human-subject results
- physical telepresence-device measurements
- validated clinical measurements
- validated psychometric outcomes
- evidence of causal relationships

---

## Controlled Fault Verification

CATEM v0.2.0 includes deterministic fault-injection tests for:

- latency
- HRV record removal
- timestamp-alignment error
- tracking dropout

Each fault is independently applied to the same unmodified baseline.

The object-drop event window and the controlled tracking-dropout fault are two distinct synthetic fixtures. The event window contains five time-indexed tracking-dropout samples (`2%`, `3%`, `15%`, `8%`, and `3%`) around the object-drop event and is used to verify event alignment and display behavior. The controlled fault test instead changes the unmodified Session 2 baseline from `4%` to `15%` to verify the system-summary response. These values serve different software-verification purposes; neither fixture represents participant data or evidence of causality.

These tests verify **software behavior and measurement-contract conformance**. They do not establish construct validity, predictive accuracy, human effectiveness, causal relationships, hardware timing accuracy, or researcher utility.

---

## Prototype Summaries

The prototype may generate layer-level summaries for software verification and visualization.

These summaries are **not validated telepresence scales** and are not presented as a universal telepresence score. Future empirical studies may omit aggregation entirely or replace prototype aggregation with a preregistered method.

---

## Tech Stack

### Frontend
- React
- TypeScript

Potential future visualization extensions:
- Recharts
- Three.js
- Framer Motion

### Backend
- FastAPI
- Python
- WebSockets

### Current Data Representation
- CSV
- JSON
- versioned schemas
- reproducibility fixtures

### Future Infrastructure Targets
- PostgreSQL
- TimescaleDB
- vector databases
- Kafka
- Redis
- Celery
- Spark Streaming

Future infrastructure targets are roadmap items unless explicitly documented in a release.

---

## CSV Format

Use `data/sample_metrics.csv` or compatible rows with fields such as:

```text
participant_id,task_type,setup,session_time,embodiment,ownership,agency,self_location,presence,social_presence,situation_awareness,trust,task_efficiency,task_completion_time,error_rate,path_efficiency,safety_events,workload,collaboration_quality,heart_rate,hrv,galvanic_response,cybersickness,latency,jitter,fps,packet_loss,tracking_dropout,visual_match,haptic_delay,timestamp_accuracy,missing_data_percent,fusion_latency,sampling_sync,autonomy_assistance,adaptation_disclosed,override_available
```

Not every field is required for every study. Expected fields, missingness rules, measurement definitions, and transformations should be specified by the study configuration and measurement contract.

---

## Run Backend

```bash
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8010
```

API: `http://127.0.0.1:8010`

## Run Frontend

```bash
cd apps/web
npm install
npm run dev
```

Web app: `http://127.0.0.1:5180`

---

## Research Platform Endpoints

- `POST /telemetry` — ingest telemetry records
- `GET /telemetry/latest` — retrieve recent telemetry events
- `WS /ws/telemetry` — development telemetry stream
- `GET /simulation/telemetry-profile` — simulator phases and configured signal generators
- `GET /simulation/telemetry-preview` — short generated telemetry sequence
- `GET /analysis` — prototype analysis outputs
- `GET /events/object-drop` — canonical five-sample object-drop fixture with 35 source records
- `GET /platform/architecture` — research platform architecture information

Any analysis outputs should be interpreted according to their registered transformation and validation status.

---

## Repository Structure

```text
apps/
  web/
  api/
  ai-engine/        # future model training/evaluation research

services/
  telemetry/
  cognition/
  embodiment/
  synchronization/
  ai-copilot/

packages/
  ui/
  types/
  analytics/

docs/
  CATEM_REPRODUCIBILITY.md
  TELEMETRY_SIMULATOR.md
  advanced_platform.md
  V1_EXECUTION_PLAN.md
  AI_PIPELINE.md
  DATA_STRATEGY.md
  DEPLOYMENT_ARCHITECTURE.md
  RESEARCH_ROADMAP.md
```

Directory names associated with future components describe intended architecture and do not by themselves imply implementation or validation.

---

## CATEM Reproducibility

Reviewer-facing materials are indexed in:

`docs/CATEM_REPRODUCIBILITY.md`

The reproducibility package should link to:

- dashboard screenshot
- sample CSV
- canonical object-drop fixture
- measurement schema
- response schema
- verification results
- version information
- exact run commands

### Reproducibility Boundary

The current package is intended to establish that the software behaves consistently with the CATEM measurement contract under the provided synthetic fixtures.

It does **not** establish:

- content validity
- construct validity
- ecological validity
- causal validity
- predictive validity
- hardware synchronization accuracy
- human-subject effectiveness
- production readiness

---

# Current Scope

CATEM v0.2.0 should be understood as:

> An executable measurement and reporting framework for organizing, synchronizing, preserving, inspecting, and exporting heterogeneous telepresence evidence.

It should **not** currently be interpreted as:

- a validated model for measuring telepresence itself
- a universal telepresence scoring system
- a causal failure-diagnosis engine
- a validated embodiment predictor
- a cognitive-state diagnostic system
- a human digital twin
- a consciousness model
- a validated autonomous HRI scientist
- a production-ready AI companion
- a validated predictive-risk system

---

# Future Research — Embodied Presence Internet

CATEM may support a broader research program called the **Embodied Presence Internet**.

The long-term goal is to investigate infrastructure for remote embodied interaction in which system, behavioral, experiential, and physiological evidence can be synchronized, preserved, analyzed, and potentially used by adaptive AI systems.

The following are **future research directions**, not CATEM v0.2.0 claims.

## 1. Real-World Telepresence Validation

Potential work:

- hardware-in-the-loop experiments
- robot telemetry
- real network conditions
- motion and tracking systems
- physiological sensors
- subjective questionnaires
- behavioral annotations
- clock-drift characterization
- network-delay characterization
- sensor synchronization testing

## 2. Human-Subject Evaluation

Potential questions:

- Does CATEM improve multimodal evidence inspection?
- Does event-centered organization reduce interpretation errors?
- Does explicit missingness improve confidence?
- Does provenance improve reproducibility?
- How should subjective experience be aligned with technical telemetry?

Human-subject work would require appropriate study design, consent, privacy protection, and institutional review where applicable.

## 3. Expert Evaluation of the Measurement Contract

Experts may evaluate:

- construct placement
- terminology
- schema completeness
- provenance requirements
- interpretation boundaries
- missing-data representation
- transformation registration
- cross-study interoperability

## 4. Multimodal Telepresence Analytics

Future datasets may combine:

- robot state
- network telemetry
- motion tracking
- eye tracking
- voice
- behavior
- physiology
- workload
- presence
- agency
- task performance

Any statistical or machine-learning model should remain a separate analysis layer with explicit assumptions, training data, transformations, and validation status.

## 5. Explainable Failure Prediction

Future research may investigate whether multimodal evidence can predict teleoperation or interaction failures using variables such as latency, jitter, packet loss, tracking degradation, workload, physiology, and task behavior.

CATEM v0.2.0 does **not** establish predictive performance.

## 6. Embodiment Modeling

Future work may investigate computational models of agency, ownership, self-location, and presence using subjective, behavioral, physiological, and system evidence.

Any such model would require independent validation.

## 7. Cognitive-State Modeling

Future research may explore probabilistic models of task-related state using workload, attention, situation awareness, stress-related signals, and task performance.

Such models should not be treated as direct measurements of internal mental states.

## 8. Human Digital Twin Representations

A longer-term direction is to investigate digital representations of a participant's time-varying interaction state using embodiment, behavior, physiology, interaction history, environment, and system conditions.

**Human digital twin** is a future research concept here, not an implemented CATEM v0.2.0 capability.

## 9. Embodied Memory Graph

Future work may investigate graph-based representations linking events, actions, system conditions, experience reports, physiological observations, transformations, provenance, and prior interaction states.

## 10. Telepresence Language-Model Assistance

Future research may investigate language models for:

- querying event windows
- summarizing available evidence
- identifying missing measurements
- explaining transformations
- retrieving provenance
- comparing sessions
- assisting research reporting

Language-model output should remain linked to underlying evidence and should not replace statistical analysis or researcher judgment.

## 11. AI-Assisted HRI Research

Possible future tasks include:

- checking dataset completeness
- locating candidate events
- comparing sessions
- detecting schema violations
- generating analysis suggestions
- preparing reproducibility reports

Any autonomous functionality would require explicit validation and human oversight.

## 12. Adaptive Telepresence

Future systems may investigate adaptation of interface presentation, autonomy assistance, communication quality, rendering strategy, or interaction timing.

Adaptive behavior should be transparent, with human override where appropriate.

## 13. Persistent Embodied Interaction

Longitudinal research may study:

- what information should persist
- what should be forgotten
- how identity should be represented
- how consent changes over time
- how provenance is maintained across sessions

## 14. Shared Remote-Presence Environments

Future work may extend event-centered evidence to:

- collaborative telepresence
- shared virtual environments
- multi-user HRI
- distributed robot teams
- remote collaboration

## 15. Full-Sensory Telepresence Research

Long-term work may investigate:

- spatial audio
- haptics
- tactile feedback
- gaze
- motion
- environmental sensing

CATEM's role would remain evidence representation, synchronization, and provenance.

## 16. Responsible AI and Privacy

Future deployments should investigate:

- informed consent
- data minimization
- access control
- retention policies
- identifier separation
- provenance
- model transparency
- participant control
- disclosure of adaptive behavior

Multimodal data involving voice, gaze, motion, physiology, and behavior may reveal information beyond the original purpose of collection.

---

# Research Roadmap

```text
CATEM v0.2.0
Synthetic software verification
        |
        v
Hardware-in-the-loop validation
        |
        v
Expert measurement-contract evaluation
        |
        v
Human-subject telepresence studies
        |
        v
Real multimodal datasets
        |
        v
Statistical / machine-learning analysis
        |
        v
Explainable predictive models
        |
        v
Adaptive telepresence
        |
        v
Longitudinal embodied interaction
        |
        v
Embodied Presence Internet
```

Each stage requires independent validation before claims from that stage should be treated as established.

---

## Research Documentation

- `docs/V1_EXECUTION_PLAN.md`
- `docs/AI_PIPELINE.md`
- `docs/DATA_STRATEGY.md`
- `docs/DEPLOYMENT_ARCHITECTURE.md`
- `docs/RESEARCH_ROADMAP.md`
- `docs/advanced_platform.md`
- `docs/TELEMETRY_SIMULATOR.md`
- `docs/CATEM_REPRODUCIBILITY.md`

`docs/CATEM_REPRODUCIBILITY.md` should be the primary reviewer-facing entry point for the CATEM paper.

---

## Versioning

The CATEM paper corresponds to:

`CATEM v0.2.0`

Research artifacts should retain explicit version information so manuscript claims can be traced to the implementation used to generate them.

Changes after a tagged research release should be documented separately rather than silently changing the evidence associated with the publication.

---

## Citation

Machine-readable citation metadata are provided in `CITATION.cff`.

If you use CATEM in research, please cite the corresponding CATEM publication once final bibliographic information is available.

---

## License

This project is open source under the MIT License. See `LICENSE`.

---

## Research Disclaimer

CATEM and the Embodied Presence Internet are research projects.

CATEM v0.2.0 provides software infrastructure for organizing and inspecting telepresence evidence. The current verification uses synthetic fixtures and does not establish clinical, psychological, causal, or predictive validity.

Future capabilities described in this repository represent research directions unless a specific version explicitly documents their implementation and validation status.
