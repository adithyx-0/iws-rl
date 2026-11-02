# PLAN v1 - three laptops, finish and present by end of day Mon 2 Nov 2026

> **Status at 2 Nov (what actually happened):** the Vivobook (M2) work was not delivered, so M1 ran it on the MacBook: no-equity x3, DQN x3, tuned CE baseline x3, fairness sweep (`models_v2/`, `results_v2/`). M1 evaluation, paired CIs, figures and `understanding.pdf` are done. M3 (Adithyan) pushed a branch `feature/adithyan-m3` with related-work, assumptions, plots and a slide outline; it is NOT merged because its cross-check and plots are v1-based and must be regenerated from `results_v2/`. Faculty approval of the topic: stated as obtained by the user. Open: slides, full-text literature check, rehearsal. Original plan text below, unchanged.

> Naming: **PLAN v1, v2, v3...** are sprints of the whole team (this file = sprint 1). `env-v2` is the *environment* git tag (demand_scale=8) and stays as is.
> Start: Sun 1 Nov ~18:00 IST. Deadline: Mon 2 Nov 23:59 IST (present-ready). Overnight = machines run, people sleep.

## 0. Goal and honest framing
Goal: a presentation with (1) a validated benchmark for equity-aware RL in intermittent water supply (IWS), (2) a fair comparison of RL vs heuristics vs an optimised fixed schedule vs a clairvoyant oracle, (3) one method contribution, (4) a clear statement of where RL helps and where it does not.

What we know today (v2 env, `results_v2/`): PPO 0.716 mean supply, CE fixed schedule 0.708, greedy_k1 0.604; PPO is NOT better than the fixed schedule on worst-zone (0.601 vs 0.612). There is a **supply ceiling** of about 0.773 (budget accounting; see `docs/reference/improvements_for_ref.md` section 2), so v1 results were saturated; on v2 the gap to the ceiling is ~0.057 (hydraulic losses + scheduling) = the headroom RL can win.

Candidate contributions (priority order; details in `docs/reference/improvements_for_ref.md` section 5):
- **C1 Adaptive policy under unknown household storage:** domain randomisation (alpha, tank size, budget) + recurrent (LSTM) policy that infers hidden tank state. Held-out parameter ranges prove generalisation.
- **C2 Equity as a constraint / welfare, shown as a Pareto front:** reward-lambda sweep vs Lagrangian worst-zone constraint; mean supply vs worst-zone curve.
- **C3 Benchmark + regime map:** when does RL beat heuristics (scarcity x hydraulic stress x tank size), with a clairvoyant oracle for regret.
We do NOT claim "unpublished" until M3's novelty check (T3.1) is done; so far we only searched titles/snippets and found no RL + IWS + equity paper.

## 1. Decision gates
- **Gate 1 (Sun 23:00, owner M1):** clairvoyant oracle vs best realistic baseline vs PPO on 30 test scenarios. If oracle - best-baseline >= 0.02 mean_sr or >= 0.05 worst-zone: headroom exists -> pursue C1 (+C2). If not: C2 + C3 become the core (regime map + Pareto), C1 becomes a negative-result note.
- **Gate 2 (Mon 12:00):** whichever models exist then are the final ones. Nothing new is started after Mon 12:00 except plots/slides/report.

## 2. Who does what (one owner per file = no collisions)

| | **M1 = MacBook (Adithya + Claude)** | **M2 = Vivobook (Adithya)** | **M3 = Adithyan (teammate)** |
|---|---|---|---|
| Branch | `core` | `compute` | `docs-analysis` |
| Role | environment, oracle, method C1, final evaluation, merging, understanding.pdf | compute + fairness C2 + baselines + learning curves | evidence: literature, assumptions, plots, slides |
| **Owns (edit only these)** | `iws_env.py`, `v2cfg.py`, `train_variant.py`, `eval_all.py`, `baselines.py`, `oracle.py`*, `train_rec.py`*, `docs/PROJECT_LOG.md`, `docs/PLAN_v*.md`, `understanding.pdf`, `docs/build_understanding.py`, `docs/understanding_source.md` | `train_fair.py`*, `fair_wrappers.py`*, `train_curves.py`*, `bo/`*, `models_fair/`, `results_M2/`, `docs/log_M2.md` | `docs/related_work.md`*, `docs/assumptions.md`*, `plots/`*, `presentation/`*, `docs/log_M3.md` |
| Compute | medium (oracle, C1 training, final eval) | **heavy** (all long training) | light; optional spare seeds |

(*) = new file/folder, created by that person.

### M1 task cards (MacBook)
1. **T1.1 Env additions (default-off, so env-v2 results stay reproducible):** `randomize=` option (draw alpha, tank_days, supply_range per episode from a train range; a *held-out* test range is fixed in `eval_all.py`), extra metrics (Jain index, CVaR10 of per-episode worst-zone, supply ceiling). Push to `core` by **Sun 20:30** so M2 can use it.
2. **T1.2 `oracle.py` (clairvoyant oracle):** the env is deterministic given the seed, so CEM over the whole 72-step action sequence per scenario = hindsight upper bound. 30 test scenarios on 9 cores ~ 10 min.
3. **T1.3 Gate 1 report** (Sun 23:00), written into `docs/PROJECT_LOG.md`.
4. **T1.4 C1:** `train_rec.py` = sb3-contrib `RecurrentPPO` (LSTM) with and without domain randomisation, 3 seeds, 200k steps, start Sun ~23:30 (overnight). If Gate 1 fails, run it anyway but report as negative result.
5. **T1.5 Final evaluation (Mon 08:30-10:30):** pull all PRs, one `eval_all.py` run for every model, paired CIs vs the *best realistic baseline*, held-out ranges, regime map.
6. **T1.6 Merging and `understanding.pdf`:** merge PRs, update the PDF at each milestone (Gate 1, overnight results, final) and ask the owner before overwriting.

### M2 task cards (Vivobook, Windows)
0. **T2.0 Setup (Sun 18:30):** Python 3.11/3.12; `git clone`; `python -m venv venv`; `venv\Scripts\activate`; `pip install -r requirements.txt`; `python check_setup.py`; **tell M1 the result and `python -c "import os;print(os.cpu_count())"`.** Windows commands: set the variable with `set IWS_V2=1` (cmd) or `$env:IWS_V2="1"` (PowerShell). If EPANET fails on Windows, say so immediately; the fallback is to run only post-processing there.
1. **T2.1 Queue:** `python run_jobs.py jobs_M2_v1.txt` (PPO-noequity x3 and DQN x3, v2 env, 300k steps; resumable: re-run the same command after any crash). Start Sun ~18:45.
2. **T2.2 Fairness / Pareto (C2):** `train_fair.py` runs PPO on v2 with `lam` in {0, 0.5, 1, 2, 4} (3 seeds each, 200k steps); then `fair_wrappers.py` = Lagrangian wrapper (dual variable on worst-zone supply >= tau) for tau in {0.55, 0.60, 0.65}. No change to `iws_env.py` is needed (`lam` is already a constructor argument). Output `models_fair/`, then M1 evaluates them. Start after T2.1 or in parallel if cores allow.
3. **T2.3 Better fixed-schedule baseline:** `bo/ce_search.py` = more iterations (40), population 60, **3 independent seeds**, honest name "CE search". Save `bo/ce_schedule_s{0,1,2}.npy`. (The old one stopped while still improving.)
4. **T2.4 Learning curves:** `train_curves.py` trains PPO v2 (3 seeds, 300k) logging evaluation every 20k steps to `results_M2/curves_s*.csv` (needed for convergence / sample-efficiency slide).
5. Commit models and CSVs on branch `compute`, open a PR every ~3 hours or when a batch finishes.

### M3 task cards (Adithyan)
1. **T3.1 Literature + novelty check (the "is it new?" evidence), Sun evening:** read the full papers (not snippets): Hendrickson & Sela 2024 (DOI in understanding.pdf), Kurian et al. 2023, MINLP equity paper (Water Supply 2023), Siddique et al. 2020 (fair RL), Cai et al. 2024 (asymmetric actor-critic). Fix the citation `69/1/184` vs `69/1/75` (see improvements_for_ref). Check that the npj Clean Water paper from the brief exists. Write `docs/related_work.md`: for each paper 3 lines (what it does / what it lacks / how we differ) + a table of every search query used (date + result) so the novelty claim is auditable. **Verify every reference; do not trust AI-written citations.**
2. **T3.2 `docs/assumptions.md`:** cited ranges for household tank size, supply hours, surge/refill behaviour; a list of every assumption and limitation.
3. **T3.3 `plots/make_plots.py`:** Pareto curve (mean vs worst-zone), bar chart with CIs per condition, regime map heatmap, learning curves, one results table. Build on `results_v2/summary.csv` and `results_v2/episodes.csv` columns now; swap inputs when final files arrive.
4. **T3.4 Slides (`presentation/`), Mon:** outline in section 5.
5. **T3.5 Confirm with the faculty that IWS-RL is the approved topic** (files 01-07 describe a different, earlier project).
6. **T3.6 Optional compute:** if >= 6 cores, `IWS_V2=1 python run_jobs.py jobs_M3_v1.txt` (PPO seeds 5-9).

## 3. Timeline (IST)
| When | M1 Mac | M2 Vivobook | M3 Adithyan |
|---|---|---|---|
| Sun 18:00-19:00 | push plan; T1.1 env | T2.0 setup, start T2.1 | clone, setup, start T3.1 |
| Sun 19:00-23:00 | T1.1 push 20:30; T1.2 oracle; Gate 1 | T2.1 running; T2.3 coded + started | T3.1, T3.2 |
| Sun 23:00-23:30 | Gate 1 decision; start overnight C1 jobs | start T2.2 fairness jobs | T3.3 plots on existing data |
| Overnight | C1 training | T2.2 + T2.4 training | (optional T3.6) |
| Mon 08:00-08:30 | pull all PRs | push models/CSVs, PR | push docs, PR |
| Mon 08:30-10:30 | **final evaluation** (T1.5) | idle -> run extra seeds if asked | plots wired to final data |
| Mon 10:30-12:00 | analyse; Gate 2 | support | slides draft |
| Mon 12:00-18:00 | understanding.pdf final, claims table | learning-curve plots | slides final, related work final |
| Mon 18:00-22:00 | rehearsal (all together), fixes | rehearsal | rehearsal |
| Mon 22:00-24:00 | buffer | buffer | buffer |

Compute rule of thumb: v2 PPO 300k steps took ~59 min with 5 runs in parallel. Run at most `cores - 1` jobs at a time. Reduce steps to 200k if a laptop is slower; **say so in the log**, because mixed step counts must be reported.

## 4. Rules (these prevent collisions and wrong numbers)
1. Edit only files you own. Need a change elsewhere? Message the owner.
2. Environment frozen: `env-v2`. M1's additions are default-off. Nobody changes dynamics.
3. Fixed protocol: test seeds 10000+, never train on them. Held-out ranges decided by M1 before training and written in `PROJECT_LOG.md`.
4. Same software versions (requirements.txt); same training seeds list per method (0-4 unless the card says otherwise).
5. Only M1 runs the final evaluation, so all numbers come from one pipeline.
6. Every model file name = `VARIANT_sSEED.zip` or `lamX_sSEED.zip`/`tauX_sSEED.zip`; folders are per owner, so nothing is overwritten.
7. Commit small, push often; PR into `main`; M1 merges. See `docs/GIT_GUIDE.md`.
8. No result goes on a slide unless it is in `results*/` and in the log.
9. If a job fails or a number looks too good, tell M1 before using it (we already found one degenerate result: scarce supply).

## 5. Presentation outline (Mon, ~12 slides)
1. Problem: intermittent water supply and inequity (real examples, cited)
2. Related work and the gap (from M3)
3. Our environment (EPANET, zones, hidden tanks, budget) and assumptions
4. Why the first version was too easy (ceiling 0.773, slack hydraulics) and how v2 fixes it
5. Methods compared: random, greedy, rota, fixed schedule, oracle, PPO, DQN, LSTM+DR
6. Main result table with CIs vs the best realistic baseline
7. Regret vs oracle and the headroom (Gate 1)
8. Equity Pareto front (C2)
9. Robustness: held-out ranges, alpha=2/8 (C1)
10. Learning curves / sample efficiency
11. Where RL does NOT help (regime map) + limitations
12. Conclusion, what is new, future work (sprint v2: second network, GNN, CVaR, cited tank data)

## 6. Risks and fallbacks
- **No oracle headroom (Gate 1 fails):** core becomes C2 + C3; message = "a tuned fixed schedule is near-optimal in this regime; here is where RL starts to help".
- **Vivobook cannot run EPANET:** M2 becomes post-processing only; M3's laptop (if strong) and M1 take the queue.
- **Overnight crash:** `run_jobs.py` resumes; check `logs/done_*.txt`.
- **LSTM does not help:** report it as a negative result.
- **Out of Claude usage:** the plan is self-contained; every task card has file names and commands; PRs can be merged by hand using `docs/GIT_GUIDE.md`.

## 7. Hand-off checklist (when a task is done)
`git add <your files> && git commit -m "..." && git push` -> open PR on GitHub -> add one line to your `docs/log_*.md`: what was run, step counts, seeds, anything odd.
