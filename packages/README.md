# Packages

Shared platform packages planned for V1.

```text
packages/
  ui/         design system components for mission-control and spatial panels
  types/      shared TypeScript and Python contract definitions
  analytics/  scoring, correlations, normalization, replay helpers
```

The web app currently has typed contracts in `apps/web/src/types.ts`; those should move into `packages/types` when shared SDK work begins.
