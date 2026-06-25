# AI Pipeline

## CATEM Measurement Contract

The dashboard implements the PDF-derived Cross-Layer Adaptive Telepresence
Evaluation Model (CATEM). Every session is evaluated across five synchronized
layers:

- Experience: ownership, agency, self-location, presence, social presence,
  situation awareness, and trust.
- Action: task efficiency, completion time, errors, path efficiency,
  collaboration quality, and movement smoothness.
- Human state: workload, heart rate, HRV, galvanic response, cybersickness,
  usability, comfort, and fatigue.
- System: latency, jitter, FPS, packet loss, tracking dropout, calibration
  error, and haptic delay.
- Data and interpretation: timestamp accuracy, missingness, fusion latency,
  sampling synchronization, visualization clarity, and explanation satisfaction.

The API returns a `catem` object for stored sessions and live telemetry. It
contains layer scores, metric coverage, synchronization/evidence quality,
live P1-P6 proposition checks, and explainable agency-preserving recommendations.

### CATEM Propositions

- P1: latency degrades agency earlier than ownership.
- P2: presence and performance can dissociate under high workload.
- P3: autonomy assistance can improve task outcomes while reducing agency.
- P4: HRV suppression or GSR elevation can precede visible instability.
- P5: gaze, gesture, and conversational synchrony can matter more than avatar fidelity.
- P6: adaptive intervention must be disclosed and overridable to preserve trust.

## V1 Baseline Models

### Embodiment Prediction Model
Inputs:
- agency
- ownership
- presence
- latency
- FPS
- packet loss
- task efficiency
- haptic delay

Outputs:
- predicted agency
- predicted ownership
- embodiment quality
- immersion collapse probability

Initial implementation:
- rule-based scoring and explainability.

Next implementation:
- logistic regression or random forest baseline.

Research implementation:
- temporal transformer or temporal graph neural network.

### Cognitive Stability Model
Inputs:
- HRV
- heart rate
- workload
- gaze drift
- motion entropy
- interaction timing
- latency

Outputs:
- overload probability
- fatigue estimate
- stress escalation state
- attention drift estimate

### Adaptive Reality Model
Inputs:
- cognitive stability
- embodiment quality
- network state
- rendering state
- haptic delay

Outputs:
- rendering quality action
- compression action
- haptic intensity action
- robot responsiveness action

## Explainability
Every prediction must return causal factors:

```json
{
  "factor": "latency",
  "value": 142,
  "impact": 0.41,
  "detail": "latency increased beyond the embodiment comfort band"
}
```

## Research Outputs
- Session summary.
- Hypothesis suggestion.
- Statistical analysis plan.
- Failure forecast.
- Adaptive intervention trace.

## Model Evaluation
- Classification metrics for collapse prediction.
- Regression error for embodiment quality.
- Time-to-event error for failure forecasting.
- Ablation by modality.
- Cross-participant generalization.
