# CATEM Prospective Empirical Validation Protocol

Status: protocol-development template; not yet preregistered or approved by an ethics committee
Software target: CATEM 0.2.0
Purpose: convert the manuscript's validation roadmap into studies that can produce empirical evidence without changing the meaning of the current synthetic verification results.

## 1. Evidence boundary

The current CATEM fixtures and telemetry cycle verify software behavior only. They are not pilot participants, physiological reference data, treatment effects, or estimates of predictive accuracy. No human, hardware, or field result may be reported until the relevant protocol is approved, executed, quality checked, and analyzed under a dated preregistration.

This template defines four linked studies:

1. expert content and weighting validity;
2. technical validation on real VR or telepresence hardware;
3. controlled human-subject construct and intervention validation; and
4. comparative utility and prospective field validation.

Each study has an independent progression gate. Failure at an earlier stage should trigger revision and retesting rather than selective reporting of later outcomes.

## 2. Shared governance and reproducibility requirements

Before collecting data:

- select the platform, task, population, sites, and intended CATEM use;
- obtain ethics and institutional approvals where required;
- preregister hypotheses, outcomes, exclusions, stopping rules, and analysis code;
- freeze the software version, API schema, transform registry, rule registry, instruments, hardware firmware, and acquisition configuration;
- calculate sample size from a declared primary estimand and justified effect or precision target;
- separate confirmatory outcomes from exploratory analyses;
- define adverse-event, simulator-sickness, loss-of-control, and withdrawal procedures;
- publish a de-identification, retention, access, and incident-response plan; and
- record protocol deviations and software/configuration hashes.

Participant counts are intentionally absent from this template. They must follow the final design, outcome variance, multiplicity plan, expected attrition, and preregistered power or precision analysis.

## 3. Study A: expert content and weighting validity

### Objective

Test whether CATEM's five layers, metric assignments, interpretation boundaries, evidence conditions, and candidate weighting strategies are understandable, complete, and defensible across disciplines.

### Panel

Recruit an independent multidisciplinary panel spanning telepresence or VR, HRI or teleoperation, human factors, measurement or psychometrics, multimodal sensing, safety, accessibility, and research data governance. Record eligibility rules, discipline, experience, conflicts, and prior involvement with CATEM. The development author should not supply the only ratings.

### Procedure

Panelists independently rate each construct, metric assignment, boundary, and required metadata field for relevance and clarity before discussion. They identify missing concepts, inappropriate aggregation, task dependencies, and unsafe interpretations. A second round follows controlled revision. If expert-derived weights are pursued, collect pairwise judgments independently and report disagreement and consistency rather than forcing consensus.

### Outcomes

- item- and scale-level content-validity summaries;
- agreement with uncertainty intervals;
- qualitative dissent and revision log;
- AHP consistency and between-expert dispersion when applicable;
- stability of weights across disciplines and use cases; and
- changes to layer membership, contracts, or boundaries.

### Progression gate

Proceed only when prespecified relevance and clarity criteria are met and unresolved dissent is explicitly documented. Expert weights remain provisional until evaluated against human and operational outcomes.

## 4. Study B: technical hardware and synchronization validation

### Objective

Determine whether CATEM records real platform signals accurately and preserves timing, provenance, missingness, and controlled faults.

### Platforms

Use at least one specified VR or telepresence configuration with versioned headset or display, tracking, input device, robot or remote endpoint where applicable, network emulator, physiological acquisition device if used, and an external timing reference.

### Bench conditions

Run repeated trials covering nominal operation and calibrated latency, jitter, packet loss, frame-rate reduction, tracking dropout, timestamp offset, sensor disconnection, and recovery. Define fault magnitudes independently of CATEM's current thresholds. Preserve raw device and network logs so CATEM records can be compared with an external reference.

### Outcomes

- timestamp offset and drift;
- end-to-end latency error and uncertainty;
- event detection sensitivity and false-alarm burden for declared software rules;
- field completeness and correctly identified missingness;
- raw-to-record and record-to-export fidelity;
- deterministic replay equivalence for captured traces; and
- performance under stream load, disconnect, reconnect, and recovery.

### Progression gate

Proceed when prespecified timing and data-integrity error budgets are met for the intended use. Version 0.2.0's in-memory storage and lack of authentication must be replaced or isolated before sensitive or multi-user collection.

## 5. Study C: controlled human-subject validation

### Objectives

1. Test convergent, discriminant, and known-groups validity of registered CATEM fields.
2. Estimate whether controlled technical or assistance conditions change the intended human and task outcomes.
3. Compare uniform weights with preregistered task-specific, expert, Bayesian, or learned alternatives without data leakage.

### Example design family

Use a randomized, counterbalanced repeated-measures or mixed design appropriate to the task. Candidate factors include network condition, display or haptic fidelity, assistance level, and adaptation disclosure or override. Do not include all factors merely because the software exposes them; select manipulations from a specific theoretical model and safety analysis.

### Measures

- validated presence, embodiment, workload, situation-awareness, sickness, usability, trust, and agency instruments selected before enrollment;
- instrument subscales, administration timing, scoring version, and minimally interpretable units;
- task completion, errors, path or control measures, safety events, assistance events, and override behavior;
- synchronized system and network traces;
- physiology only with acquisition, baseline, artifact, exclusion, and interpretation procedures; and
- participant characteristics justified by the research question.

### Analysis

- declare one primary estimand and control multiplicity for confirmatory secondary outcomes;
- use models matching the repeated or clustered design;
- report estimates, uncertainty intervals, missingness, exclusions, and robustness analyses;
- test convergent and discriminant patterns without treating layer membership as proof of a latent construct;
- compare weighting strategies on held-out participants or sites;
- nest all feature selection, transform tuning, and weight learning inside resampling;
- report calibration and subgroup results when prediction is evaluated; and
- retain the uniform and original-metric baselines.

Layer scores should not replace original instruments in the primary scientific report. A weighting method should advance only if it improves a preregistered criterion, remains stable under sensitivity analysis, and does not obscure safety-relevant or construct-specific results.

### Progression gate

Proceed when manipulation checks succeed, measurement hypotheses are supported to the preregistered standard, adverse-event rules are satisfied, and any predictive or weighting result replicates on held-out data.

## 6. Study D: comparative utility and field validation

### Comparative interpretation study

Use matched session evidence to compare CATEM with a conventional multimodal
dashboard and prespecified single-domain baselines such as latency-only,
task-only, or questionnaire-only reports. Prefer a within-evaluator,
counterbalanced crossover when learning and carryover can be measured and
controlled; otherwise use a randomized parallel design. Hold the underlying
session data, display time, training, task prompts, and available evidence
constant across conditions. Balance condition and session order, separate
training from scored trials, and preregister washout or carryover procedures.

Create the reference interpretation before evaluator enrollment through an
independent adjudication panel that is blinded to interface condition. Score
responses using a frozen rubric and blinded assessors. Declare the difference
in interpretation accuracy as the primary estimand. Calculate evaluator count
from the final design, expected within-evaluator or between-group variance,
minimum relevant difference, multiplicity plan, attrition, and preregistered
power or precision target; do not justify sample size from convenience alone.

Measure:

- interpretation accuracy and consistency;
- time to identify a declared cross-layer event;
- unsupported causal or diagnostic conclusions;
- confidence calibration;
- traceability of the stated evidence;
- workload and usability; and
- disagreement resolution.

Analyze the primary outcome with a model appropriate to the crossover,
repeated, or parallel design. Include evaluator and session effects where
applicable, test period and order effects, report carryover sensitivity, and
retain all prespecified baseline conditions. Report estimates and uncertainty
intervals rather than relying only on significance tests. Interface preference
or faster completion must not substitute for accurate, bounded interpretation.

### Prospective deployment

After controlled validation, deploy a frozen version prospectively on the intended platform. Monitor availability, data drift, missingness, false alarms, override use, privacy incidents, adverse events, operator burden, and maintenance. Do not silently update transformations, thresholds, or weights during an evaluation period.

### Progression gate

Claim practical utility only if CATEM improves a prespecified evaluator or operational outcome against the selected baseline without unacceptable burden, safety risk, privacy loss, or loss of interpretability.

## 7. Minimum release artifacts for every study

- dated protocol and registration identifier;
- ethics approval or documented determination;
- analysis plan and executable code;
- software, schema, registry, configuration, and hardware versions;
- de-identified data dictionary and permitted data or synthetic surrogate;
- recruitment, exclusion, attrition, and deviation accounting;
- complete outcome and adverse-event reporting;
- weighting and threshold sensitivity results;
- machine-readable CATEM exports and validation logs; and
- persistent archive identifier and license.

## 8. Reporting language

Until these studies are completed, use "software verified," "synthetic demonstration," "rule activation," or "prospective validation." Reserve "validated," "predictive," "diagnostic," "effective," and "safe" for claims directly supported by the corresponding preregistered evidence.
