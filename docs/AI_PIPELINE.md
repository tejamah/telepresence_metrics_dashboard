# AI Pipeline

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
