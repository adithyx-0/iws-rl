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

## 2026-11-01 (later) - RL prior art, slide draft, faculty message
- Checked Hu 2020 (MBE), Hu/Gao/Zhong 2023 (Water Supply 23(7)), DRL-EPANET (NeurIPS-W 2022, JWRPM 2024): bibliographic data confirmed, abstract-level only. `docs/related_work.md` section 2 updated.
- New lead: a "CORE" preprint on per-household refill thresholds in IWS (UNVERIFIED, seen in a search snippet). Must be read before any novelty wording is used.
- `presentation/outline.md`: 12-slide content draft; TBD slides wait on M1 final eval and M2 models.
- `docs/faculty_message.md`: draft of T3.5 message, NOT sent.
- Push to GitHub blocked by 403 (stale cached credentials); commits are local only.

## 2026-11-01 (night) - CORE resolved, compute blocked
- CORE preprint read at abstract-page level (engrXiv 7798): household pump thresholds, no RL/zone/equity. Not a threat to the novelty wording. `docs/related_work.md` updated.
- Hubli-Dharwad tank-volume numbers: not obtained (eScholarship empty, NSF PAR refused). Leads: PMC4624240, Water Alternatives 2014 storage paper.
- T3.6 spare PPO seeds 5-9: NOT started. This machine has 12 cores but no venv and no stable-baselines3/sb3-contrib; needs `python -m venv venv` + `pip install -r requirements.txt` (large torch download). Waiting for a decision.

## 2026-11-02 - T3.6 spare PPO seeds 5-9 (v2 env, 300k steps): status
**Setup (Windows):** Smart App Control blocked PyTorch DLLs (WinError 4551); user turned it off (irreversible without a Windows reset). venv created, `requirements.txt` installed plus `six` (wntr 1.5.0 imports it but does not declare it). `check_setup.py` passes.
**Finished:** seeds 5, 6, 7, 9 -> `models_v2/ppo_s{5,6,7,9}.zip` (300k steps, `IWS_V2=1`, same command as seeds 0-4: `train_variant.py ppo SEED 300000`). Wall time 7,261-8,925 s each with 5 jobs in parallel on 12 cores. Smoke test only (all four load; scenario 10000 mean_sr 0.731-0.745): NOT an evaluation. Final numbers must come from M1's `eval_all.py`. The new .zip files are untracked on purpose.
**Seed 8:** my attempts failed twice (EPANET 305 at ~77 min) then stopped silently; a third attempt (own folder, own TEMP, `D:\projects\iws-rl_runs\s8_retry2`) started 2026-11-02 18:39. SEPARATELY, an untracked `models_v2/ppo_s8.zip` (mtime 11:43 on 2026-11-02) was already in the repo folder when I checked at 18:40; I did not create it and do not know its provenance, so I did not overwrite it and have not validated it. Seeds 5, 6, 7, 9 are mine.
**Windows problems found (for M1, who owns `run_jobs.py`, `iws_env.py`, `train_variant.py`):**
1. Five jobs started together from `run_jobs.py` in the repo folder: four crashed within 30 s with EPANET error 307 "cannot read hydraulics file". The explanation that they shared a working directory is NOT confirmed.
2. Re-run in separate folders: seed 5 crashed at ~51 min and seed 8 at ~77 min with EPANET error 305 "cannot open hydraulics file", so separate folders do not prevent it. Cause unknown; a shared Windows TEMP folder (hundreds of `iws_*` files) is untested suspicion.
3. A seed-8 retry with its own TEMP stopped without any error or output after ~3.5 h. Cause unknown.
4. No checkpointing: every crash loses the whole run. Suggested fixes (M1's call): retry on EpanetException, periodic `model.save`, per-environment temp folders.
**Method used for the successful runs:** detached hidden processes, `IWS_V2=1`, one working folder per seed under `D:\projects\iws-rl_runs\` (outside the repo). Seed 5 needed a second attempt.

## 2026-11-02 - plots and slide outline refreshed on M1's final results
- `plots/make_plots.py`: new `--lambda-sweep` option (PPO lambda sweep from `summary.csv`), labels for `ce_tuned` and lambda families, UTF-8 table output. Regenerated `plots/out/` with `--baseline ce_tuned --lambda-sweep` (default condition, 18 methods, scarce excluded from heatmaps).
- `presentation/outline.md` rewritten: the old story (PPO about equal to the CE schedule) was based on the early 1-seed CE schedule. With the tuned schedule: PPO ties on mean supply, loses on worst zone (-0.030) and return (-0.52, M1's paired CIs); RL wins only at alpha=2 (all three RL methods) and DQN at small tanks. Slide 10 (learning curves): NO DATA in repo. Oracle row uses 30 scenarios vs 100 for the rest: flagged on the slide.
- `docs/assumptions.md`: stale statements about the CE schedule and the greedy_k1 comparison corrected.
- Not checked: M1's `results_v2/figs/` (M1's own figures) were not compared with mine; table values match M1's README.
