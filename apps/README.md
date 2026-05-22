# Apps

V1 application boundaries for Embodied Presence Infrastructure.

```text
apps/
  web/       React + TypeScript experience layer
  api/       FastAPI platform API
  ai-engine/ model training, evaluation, and inference services
```

The current runnable prototype still lives in `frontend/` and `backend/`. The migration path is to move those folders into `apps/web` and `apps/api` once the TypeScript and service contracts stabilize.
