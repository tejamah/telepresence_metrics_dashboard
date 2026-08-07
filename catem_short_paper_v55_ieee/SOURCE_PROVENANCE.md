# Source provenance

This IEEE short-paper conversion uses `C:\Users\tejam\Downloads\catem_short_paper__55_ (2).pdf` as its sole scientific-content source.

The conversion removes the table of contents, repairs obvious PDF conversion artifacts, restores equation notation and citation typography, and places the supplied material in the official IEEE conference class. It does not introduce new measurements, experimental records, model outputs, claims, references, or generated data.

The supplied PDF contains no rendered framework or dashboard figures and exposes two controlled-response rows in Table I. The original IEEE conversion therefore did not add the missing figures or unseen table values.

At the author's request on 2026-08-05, the IEEE source was supplemented with the existing verified dashboard capture at `docs/catem/dashboard_overview_full.png`. The paper presents two crops of that single capture: the synthetic live-session/four-layer assessment and the synthetic object-drop evidence window. No new measurements, table values, or scientific claims were introduced.

Also at the author's request on 2026-08-05, Table I was expanded with the existing timestamp-offset fault-injection result recorded in `docs/catem/verification_results.json`: timestamp error was set to 30 ms and synchronization quality decreased from 75.9 to 54.3. The value was copied from the versioned verification artifact; it was not newly generated for the manuscript.

On 2026-08-06, all four Table I rows were regenerated from the same unmodified Session 2 baseline with the public v0.2.0 verification harness. The fresh raw harness outputs are stored in `verification/verification_results.json` and `.csv`; `verification/table_i_verification.json` and `.csv` explicitly record the baseline and modified inputs, corresponding outputs, public-tag commit, source hashes, and unchanged fixture hash. The evidence exporter also checks every rendered Table I cell against these values.

The author subsequently requested explicit responses to anticipated novelty and evaluation questions. The revised text distinguishes the executable lifecycle contract from schemas, ontologies, and multimodal data models, and limits the evidence claim to software conformance properties tested by the verification harness. It explicitly states that software verification is insufficient for scientific validity, practical effectiveness, generalizability, causal explanation, or researcher utility. No new empirical evidence or validation claim was added.
