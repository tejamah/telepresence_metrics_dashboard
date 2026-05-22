# Packages

Shared platform packages planned for V1.

```text
packages/
  ui/         design system components for mission-control and spatial panels
  types/      shared TypeScript and Python contract definitions
  analytics/  scoring, correlations, normalization, replay helpers
```

The frontend now has typed contracts in `frontend/src/types.ts`; those should move into `packages/types` when the monorepo migration begins.
