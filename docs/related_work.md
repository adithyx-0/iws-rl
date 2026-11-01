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

## 2. Closest RL work (no equity, not IWS) - UNVERIFIED
Carried over from `docs/PROJECT_LOG.md` (titles/snippets only; nobody has read these): Hu et al. 2020 (DRL valve scheduling for contamination), Hu/Gao/Zhong 2023 (MADDPG pump+valve), DRL-EPANET 2022, PPO pump scheduling 2023. TODO: find exact references and confirm each lacks equity and intermittent supply.

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

TODO for a human: open each DOI/arXiv link, read the full text, then upgrade the flag to `VERIFIED-FULLTEXT` and add one concrete sentence (their metric, their network, their result).
