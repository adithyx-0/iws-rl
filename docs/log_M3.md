# M3 log (Adithyan, branch `feature/adithyan-docs-analysis`)

## 2026-11-01 - T3.1, T3.2, T3.3 first drafts
Files added (all new, no existing file edited): `docs/related_work.md`, `docs/assumptions.md`, `plots/make_plots.py`, `plots/out/*`, this log.

### What was checked
- Web searches (standard mode, abstracts/snippets only; no full paper read). Queries and results are in `docs/related_work.md` section 6.
- **Citation fix found:** MDPI Eng. Proc. 69/1/75 = Hendrickson & Sela. 69/1/184 = the Adhityan R / Kurian / Narasimhan data-driven paper. `docs/PROJECT_LOG.md` (M1's file) says 69/1/184 for Hendrickson & Sela: **needs correcting by M1**.
- Siddique et al. (ICML 2020) and Cai et al. (NeurIPS 2024): titles, authors, arXiv IDs confirmed. The Cai paper's real title is "Provable Partially Observable RL with Privileged Information".
- "npj Clean Water Sept 2026" paper from the brief: not found, not re-searched deeply. Treat as unconfirmed.
- Household tank size: no measured survey found; vendor norms suggest ~2 days of storage versus our 0.3-0.8 days. Flagged as a limitation.

### Plot script
- Run: `python plots/make_plots.py` (defaults to `results_v2/`, baseline `ce_schedule`, condition `default`).
- Re-point at final data: `--results-dir DIR`, or `--summary`, `--episodes`, `--oracle` individually; `--out-dir` for the output folder; `--pareto CSV` (columns `label, mean_sr, min_zone_sr`) and `--curves "GLOB"` (columns `step, mean_sr`) when M2's files exist.
- The scarce condition is dropped from heatmaps by default (degenerate); `--include-scarce` keeps it.
- Heatmap values are paired per-scenario mean differences vs the baseline, without CIs.
- Output is read-only on result files. Not yet tested: Pareto and learning-curve branches (no input files exist).
- Current v2 output: PPO 0.716 vs CE schedule 0.708 mean supply, PPO 0.601 vs CE 0.612 worst-zone. Only 1 seed of CE schedule and the baselines; M2's 3-seed CE rerun and the noequity/DQN models are not in `results_v2/` yet.

### Open items
1. A human must open the DOIs/arXiv links and upgrade flags to VERIFIED-FULLTEXT.
2. Faculty confirmation that IWS-RL is the approved topic (T3.5): message to send, not a file.
3. Slides (T3.4): deferred until final numbers exist.
4. When M1's final `eval_all.py` output lands, rerun plots with `--results-dir` and replace `plots/out/`.
