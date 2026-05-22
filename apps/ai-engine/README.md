# AI Engine

Research and inference workspace for Embodied Presence Infrastructure.

## V1 Responsibilities
- Train/evaluate baseline embodiment prediction models.
- Train/evaluate cognitive stability models.
- Generate offline model reports from exported datasets.
- Provide future inference adapters for the FastAPI app.

## Planned Structure

```text
apps/ai-engine/
  models/        model definitions and baselines
  pipelines/     training and evaluation pipelines
  notebooks/     research exploration
  reports/       generated evaluation summaries
```

The current V1 implementation uses rule-based models in `apps/api/routes.py`; this app is the extraction point for ML baselines.
