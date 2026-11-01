> **Superseded by `docs/PLAN_v1.md` (3 laptops: M1 MacBook, M2 Vivobook, M3 Adithyan).** Kept for reference.

# Three-way work split (3 laptops)

Goal: finish a strong IWS-RL project faster by running independent work in parallel, with **no two people editing the same file**.
Merging is done on GitHub with pull requests (see `GIT_GUIDE.md`). Because everyone owns different files, there should be no merge conflicts.

## The three workstreams

| | Laptop A - CORE (Adithya + Claude) | Laptop B - teammate (writing/analysis) | Laptop C - COMPUTE (Adithya's 2nd laptop) |
|---|---|---|---|
| Branch | `core` | `docs-analysis` | `compute` |
| Owns (only this person edits) | `iws_env.py`, `train_variant.py`, `eval_all.py`, `v2cfg.py`, `baselines.py`, `docs/PROJECT_LOG.md`, `docs/ROADMAP.md` | `docs/related_work.md`, `docs/assumptions.md`, `plots/` (new folder), `networks_extra.py` (new file) | `models_v2/` files it trains, `bo/` (new folder), `docs/log_C.md` |
| Tasks | 1. Evaluate v2 + confirm pressure matters. 2. Domain randomisation with held-out ranges. 3. Lagrangian worst-zone constraint + Pareto curve over lambda. 4. Final evaluation, paired CIs vs best baseline. | 1. Read full papers: Hendrickson & Sela, MINLP equity paper (Water Supply 2023), Kurian et al.; write `docs/related_work.md` (what exists, what we add). 2. Find cited household tank sizes / storage numbers -> `docs/assumptions.md` with references. 3. Plot scripts (learning curves, sensitivity, one results table) built on `results/summary.csv`. 4. Second network: load another WNTR example network, zone it, run baselines (new file only). | 1. Train the 6 v2 runs in `jobs_v2_laptopC.txt` (PPO-noequity x3, DQN x3). 2. Proper Bayesian-optimisation fixed-schedule baseline (multi-seed) in `bo/`. 3. Tune A2C or decide to drop it. 4. Extra seeds 5-9 for final methods once core posts the final config. |
| Compute | light | light | heavy (all training) |

## Rules (this is what prevents errors)
1. **Environment is frozen at git tag `env-v2`** after Laptop A confirms v2. Nobody changes the environment without telling the others.
2. **Fixed evaluation protocol:** test scenarios are seeds 10000+, conditions as in `eval_all.py`. Never evaluate on training seeds (0-9999).
3. **Same software:** Python 3.11/3.12, `pip install -r requirements.txt` (pinned versions). Run `python check_setup.py` first.
4. **Model file names are `VARIANT_sSEED.zip`; jobs are disjoint** (see job files), so two laptops never write the same file.
5. **Only Laptop A runs the final evaluation** (`eval_all.py`) after pulling everyone's models. This keeps all numbers computed one way.
6. **Each person logs in their own file** (`docs/log_A.md`-style); only Laptop A edits `PROJECT_LOG.md` (summarising the others).
7. If you need a change in a file you don't own, message the owner; do not edit it.

## How the pieces are combined
1. Each person works on their own branch and opens a Pull Request (PR) into `main` when a task is done.
2. Laptop A reviews and merges the PRs (the green button on GitHub).
3. Everyone runs `git switch main && git pull` before starting new work.
4. Order of merging does not matter, because the files are disjoint.

## Timeline (rough)
- Now: A finishes the v2 PPO runs and evaluates; B starts reading; C runs `jobs_v2_laptopC.txt`.
- After `env-v2` tag: C starts BO/A2C; B starts second network; A starts domain randomisation + Lagrangian.
- End: A merges all, runs final evaluation, B/C plots and writing.
