# Embodied Presence Internet Dashboard v3

## Reference

This version follows the supplied `Embodied Presence Internet3.pdf`, an 11-page browser rendering created on August 9, 2026. The reference defines the complete dashboard presentation rather than a new CATEM scientific result.

The current repository rendering is preserved in [`embodied_presence_internet_dashboard_v3.pdf`](embodied_presence_internet_dashboard_v3.pdf). It was regenerated from the implementation on `main` after the terminology review described below.

## Included dashboard surface

The version retains the reference dashboard's major sections:

1. mission control and live synthetic telemetry;
2. four CATEM observational layers;
3. the separate cross-cutting Data and Interpretation Conditions band, explicitly marked as not an observational layer;
4. the canonical object-drop window with five offsets, seven measures, and 35 traceable records;
5. CATEM propositions and agency-preserving review prompts;
6. an explicit boundary before experimental future-work modules;
7. live heuristic streams and the synthetic telemetry simulator;
8. multimodal, heuristic participant-profile, sensory, shared-reality, and adaptation prototype panels;
9. descriptive rule traces and hypothesis prompts;
10. core metrics and insufficient-sample analytics; and
11. the experimental research architecture and session comparison table.

The live simulator changes values over time, so regenerated dashboard PDFs may show a different active session or live frame while preserving the same authored fixtures, layout, contracts, and interpretation boundaries.

## Scientific boundary

Pages containing the four CATEM layers, the separate \(D_t\) condition band, and the canonical event window are the dashboard evidence corresponding to the submitted CATEM paper. Experimental modules later in the dashboard are future-work prototypes and are not paper contributions, validated predictive models, diagnostic tools, or causal evidence.

The supplied August 9 rendering used prediction-like wording in one experimental card. The current v3 implementation intentionally corrects that language:

- `Failure Forecast Heuristic` is presented as `Rule-Based Risk Review`;
- no time-to-event value is produced;
- no predictive confidence or probability is produced;
- status is limited to a deterministic `nominal` or `elevated` input condition;
- outputs are review prompts rather than autonomous interventions; and
- the card states that no event timing or probability is estimated.

This terminology correction preserves the reference layout while keeping the dashboard consistent with the submitted paper's statement that no predictive model was trained.

The participant profile now identifies its state as a heuristic label, presents fatigue only as a prototype indicator, qualifies two-session relationships as candidate fixture patterns, and names the final composite column `Prototype summary`.

## Reproduce

Start the API and dashboard from the repository root:

```bash
cd apps/api
python run_server.py
```

In a second terminal:

```bash
cd apps/web
npm run dev
```

Open `http://127.0.0.1:5180`. The committed PDF was generated from that local page after confirming that the API, metrics endpoint, and dashboard each returned HTTP 200.

## Verification

The paper-version implementation retains the original 17-check CATEM v0.2.0 software-verification result. The separate `catem-validation-v1` branch retains the later 39-check synthetic ground-truth suite and 33-check end-to-end pipeline suite.
