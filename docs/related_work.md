# Related work and novelty check (M3, T3.1)

**Status: DRAFT from abstracts and search snippets, 2026-11-01.** Full texts have NOT been read. Every entry has a
verification flag. Do not put a claim on a slide unless its flag is `VERIFIED-FULLTEXT`.
Flags: `ABSTRACT-ONLY` (bibliographic data confirmed by search, details from abstract), `UNVERIFIED` (not found or not checked).

## 1. Closest prior work (non-RL, same problem)

### Hendrickson & Sela (2024) - ABSTRACT-ONLY
- Venue: *Sustainable Cities and Society*, "Optimizing equity in intermittent water supply systems: A volume-driven demand and flow control approach" (journal, 2024). Conference version: MDPI *Engineering Proceedings* vol. 69, no. 1, article **75** (https://www.mdpi.com/2673-4591/69/1/75).
- Does: simulation-optimisation with volume-driven demand; Bayesian optimisation of flow-control-valve schedules to maximise local supply and global equity. Private tanks are modelled and said to worsen inequity. States that real-time tank level data is not needed.
- Lacks: an open-loop optimised schedule (not a closed-loop policy that reacts to observations); no learned policy.
- How we differ: closed-loop RL policy with hidden household tanks; we also compare against an open-loop optimised schedule (our `ce_schedule`), which is the closest analogue of their method. We did NOT implement their Bayesian optimisation (our baseline uses cross-entropy search).
- **Citation fix:** `docs/PROJECT_LOG.md` cites this as "69/1/184". Search results show 69/1/75 is Hendrickson & Sela and 69/1/184 is a different paper (see below). The log should say 69/1/75. (Log is owned by M1: tell them.)

### Kurian et al. (2023) - ABSTRACT-ONLY
- *Water Supply* (IWA) vol. 23, no. 11, pp. 4520-4538, Nov 2023: "Equitable supply in intermittently operated rural water networks in emerging economies".
- Does: MINLP that minimises supply inequity subject to hydraulics, hours-of-supply and valve-operation constraints; validated by simulation of a central-India network (107 villages, one source) and a laboratory network.
- Lacks: optimisation per known demand/schedule; no learning; no uncertainty about household storage.
- How we differ: learned reactive policy under stochastic budget and hidden storage.

### Adhityan R, Kurian, Narasimhan - data-driven equitable supply - ABSTRACT-ONLY
- WDSA-CCWI 2022 proceedings (published 2024); MDPI *Eng. Proc.* 69/1/184 per search results. A data-driven approach to scheduling supply for equity.
- Probably the paper the project log meant by "69/1/184". Authors/title to be confirmed from the page.

### Gullotta et al. (2021) - ABSTRACT-ONLY (found incidentally)
- *J. Water Resour. Plann. Manage.* 147(5): "Optimal Location of Valves to Improve Equity in Intermittent Water Distribution Systems". NSGA-II + EPA-SWMM, networks with private tanks. Design-time (valve placement), not operation.

## 2. Closest RL work (no equity, not IWS) - ABSTRACT-ONLY (checked 2026-11-01)
- **Hu, Cai, Zeng, Yan, Gong, Wang (2020)**, "Deep reinforcement learning based valve scheduling for pollution isolation in water distribution network", *Math. Biosci. Eng.* 17(1):105-121, doi 10.3934/mbe.2020006. State = sensor readings, actions = valve/hydrant operations, EPANET. Goal is contaminant isolation, not supply rationing or equity.
- **Hu, Gao, Zhong (2023)**, "Multi-agent reinforcement learning framework for real-time scheduling of pump and valve in water distribution networks", *Water Supply* 23(7):2833-2846, doi 10.2166/ws.2023.163. MADDPG, beats GA/PSO/DE; objective is water loss and energy. No equity, no intermittent supply. (One index lists an arXiv ID 2408.08442 that may not match; use the DOI.)
- **DRL-EPANET** (Belfadil, Modesto et al.): NeurIPS 2022 workshop paper; journal version *J. Water Resour. Plann. Manage.* 150(2), 2024, "Leveraging Deep Reinforcement Learning for Water Distribution Systems with Large Action Spaces and Uncertainties". Pressure control with branching dueling Q-networks on 10 real networks. Not intermittent supply, not equity.
- **"CORE" preprint (UNVERIFIED, title/authors unknown):** a search snippet describes a preprint on per-household adaptive refill thresholds for pump scheduling in intermittent supply. Not RL on zone scheduling as far as the snippet says, but it concerns household storage in IWS. **Find it and read it before claiming novelty.**
- "PPO pump scheduling 2023" from M1's log: not re-found; reference still unconfirmed.
- A 2026 *Water Research X* DRL+EPANET contamination paper was also mentioned in results; irrelevant to equity.

## 3. Methods papers we rely on

### Siddique, Weng, Zimmer (ICML 2020) - ABSTRACT-ONLY
- "Learning Fair Policies in Multi-Objective (Deep) Reinforcement Learning with Average and Discounted Rewards", ICML 2020 (arXiv 2008.07773).
- Does: optimises a generalised Gini welfare over per-user utility vectors, adapting deep RL algorithms; discusses discounted vs average rewards.
- Relevance: our "worst-zone supply" objective is a max-min welfare. Their framing supports the lambda sweep (C2).
- Caveat to state: our fairness term is applied to per-day zone supply ratios inside the reward; welfare of expected return and expected welfare are different quantities. Do not claim our policy is "max-min optimal".

### Cai, Liu, Oikonomou, Zhang (NeurIPS 2024) - ABSTRACT-ONLY
- "Provable Partially Observable Reinforcement Learning with Privileged Information", NeurIPS 2024 (arXiv 2412.00985).
- Does: analyses expert distillation (teacher-student) and asymmetric actor-critic when privileged state is available in training.
- Relevance: hidden household tank levels are exactly such privileged information (our simulator knows them, the utility does not). Motivates the LSTM (C1) and a possible asymmetric critic. Our `priv_greedy_k1` is a privileged heuristic, not a distilled teacher.
- Earlier plan text called this "Cai et al. 2024 (asymmetric actor-critic)": the real title is the one above.

## 4. Not yet checked
- The "npj Clean Water, Sept 2026" equity paper named in the project brief: **not found** by the earlier search and not re-checked here. Treat as nonexistent until someone produces a link.
- 2023 *Water Supply* MINLP equity paper: probably the same as Kurian et al. above; confirm it is not a second paper.
- Fair-RL welfare-nonlinearity papers (arXiv 2606.18111, 2608.00175) cited in `docs/reference/improvements_for_ref.md`: IDs not verified here.

## 5. Novelty statement (what we may say)
Allowed: "In our search (table below) we did not find an RL paper that combines intermittent supply, zone-open/close scheduling, equity, and hidden household storage."
Not allowed: "this is the first / unpublished". The search covered a handful of queries and abstracts only.

## 6. Search log (for auditability)
| Date | Query (abridged) | Result |
|---|---|---|
| 2026-11-01 | Hendrickson Sela Bayesian optimization flow control valve intermittent equity private tanks | Found journal paper + MDPI 69/1/75; also Gullotta 2021 |
| 2026-11-01 | Kurian intermittent water supply equity MINLP rural India Water Supply 2023 | Found Kurian 2023; MDPI 69/1/184 belongs to the data-driven follow-up |
| 2026-11-01 | Siddique Weng Zimmer fair policies ICML 2020 | Confirmed; arXiv 2008.07773 |
| 2026-11-01 | Cai asymmetric actor-critic privileged information NeurIPS 2024 | Confirmed title/authors; arXiv 2412.00985 |
| earlier (M1) | RL + intermittent supply + equity + valve scheduling | No match (titles/snippets only) |
| 2026-11-01 | Hu deep RL valve scheduling water distribution contamination 2020 | Found Hu et al. 2020 (MBE) |
| 2026-11-01 | MADDPG pump and valve scheduling Hu Gao Zhong 2023 | Found, Water Supply 23(7) |
| 2026-11-01 | reinforcement learning intermittent water supply equity zone valve scheduling household storage | No direct match; surfaced the unverified "CORE" household-refill preprint |
| 2026-11-01 | DRL-EPANET NeurIPS 2022 | Found workshop + JWRPM 2024 versions |

TODO for a human: open each DOI/arXiv link, read the full text, then upgrade the flag to `VERIFIED-FULLTEXT` and add one concrete sentence (their metric, their network, their result).
