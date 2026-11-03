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
- **DRL-EPANET** (Belfadil, Modesto et al.): NeurIPS 2022 workshop paper; journal version *J. Water Resour. Plann. Manage.* 150(2), 2024, "Leveraging Deep Reinforcement Learning for Water Distribution Systems with Large Action Spaces and Uncertainties". Pressure control with branching dueling Q-networks on 10 real networks. Not intermittent supply, not equity. Author note (Part B): the journal paper has six authors (Belfadil, Modesto, Meseguer, Joseph-Duran, Saporta, Martin Hernandez); the three-author version is the NeurIPS 2022 workshop paper.
- **CORE (Pentyala et al., engrXiv preprint, posted 2026-08-03, DOI 10.31224/7798) - ABSTRACT-ONLY, preprint, peer-review status not stated:** "CORE: Household-Learned Adaptive Thresholds for Pump Scheduling in Intermittent Water Supply Systems". Sets a per-household, per-hour pump trigger from that household's own history; tested on 100 households over 90 days (synthetic demand + Alicante smart-meter data). No RL, no zone/valve scheduling, no equity analysis per the abstract page. Closest on "household storage in IWS" but a different decision problem (household pump, not utility zone scheduling). Does not change our novelty wording.
- "PPO pump scheduling 2023" from M1's log: not re-found; reference still unconfirmed.
- A 2026 *Water Research X* DRL+EPANET contamination paper was also mentioned in results; irrelevant to equity.

## 3. Methods papers we rely on

### Siddique, Weng, Zimmer (ICML 2020) - ABSTRACT-ONLY
- "Learning Fair Policies in Multi-Objective (Deep) Reinforcement Learning with Average and Discounted Rewards", ICML 2020 (arXiv 2008.07773).
- Does: optimises a generalised Gini welfare over per-user utility vectors, adapting deep RL algorithms; discusses discounted vs average rewards.
- Relevance (corrected): our equity term is a scalar bonus lambda x (worst-zone supply ratio), added once per day to a utilitarian per-hour reward. It is closest to the max-min special case of their framework but is NOT their GGF optimisation over the vector of per-user expected returns (Part B, B1). Use their work as the conceptual reference for fair RL; a GGF-PPO baseline would be the proper comparison.
- Caveat to state: our fairness term is applied to per-day zone supply ratios inside the reward; welfare of expected return and expected welfare are different quantities. Do not claim our policy is "max-min optimal".

### Cai, Liu, Oikonomou, Zhang (NeurIPS 2024) - ABSTRACT-ONLY
- "Provable Partially Observable Reinforcement Learning with Privileged Information", NeurIPS 2024 (arXiv 2412.00985).
- Does: analyses expert distillation (teacher-student) and asymmetric actor-critic when privileged state is available in training.
- Relevance: hidden household tank levels are exactly such privileged information (our simulator knows them, the utility does not). Motivates the LSTM (C1) and a possible asymmetric critic. Our `priv_greedy_k1` is a privileged heuristic, not a distilled teacher.
- Earlier plan text called this "Cai et al. 2024 (asymmetric actor-critic)": the real title is the one above.

## 4. Not yet checked
- **"npj Clean Water" equity paper (CORRECTED 2026-11-02 from the Part B results supplied by the user; I have NOT opened it):** reported to exist: "Equitable supply in water distribution networks using data-driven optimization and AI-assisted voice automation", *npj Clean Water*, dated 21 Sep 2026 (seen on the nature.com subject listing only). Authors and methods unverified. It is probably related to the Kurian et al. MILP / data-driven line (inference, not verified). Our earlier statement "not found" was wrong. **Read it before using any novelty wording.** The Huang et al. 2025 npj paper (DOI 10.1038/s41545-025-00512-z) is urban drainage, not supply.
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

## 7. Added from the Part B verification results (supplied by the user, 2026-11-02; NOT independently checked by me)
Source: the "Verification results: PART B" text the user pasted into the session. The repo file `docs/verify/results_ADITHYAN.md` is an OLDER version of it; replace it with the newer text. Statuses below are the ones that text gives.
- **Siddique et al. 2020 (FULL read there):** optimises generalized Gini welfare over the vector of per-user expected returns; adapts DQN, A2C, PPO; no water application; 50/20 seeds.
- **Hu, Gao, Zhong 2023 (abstract only):** MADDPG pump+valve, energy and water-loss cost, no equity. Do not confuse with Hu et al. 2023, *Systems* 11(2):56 (exploration-enhanced PPO for pumps).
- **Pei, Hoang, Fu, Butler 2025 (abstract + GitHub):** PPO for real-time pump scheduling, JWRPM 151(6): 04025012; beats robust optimisation under demand uncertainty; continuous supply, cost objective. Supports PPO in this domain; not equity.
- **Hajgato, Paal, Gyires-Toth 2020 (FULL read there):** dueling DQN for pump speed, randomised demand scenarios, tests drawn from the SAME distribution as training. Our held-out parameter ranges are a differentiator.
- **Gym4ReaL (Salaorni et al. 2025, WDSEnv mostly read):** DQN vs rule-based pump policies on Anytown, aggregate demand-satisfaction reward, no tuned fixed schedule, no equity, no unseen-regime test.
- **Hendrickson & Sela 2024 (FULL read there):** volume-driven-demand tanks, supply hierarchy (favourable consumers fill first), Bayesian-optimised open-loop valve schedules (100 iterations), medium network 6 zones, 8 h supply/day: equity 0.61 to 0.78, supply ratio 0.79 to 0.87; tank-size sensitivity +-50%. The analogue of our tuned fixed schedule.
- **Sarisen et al. 2026 (WRR):** uncertainty in IWS simulation from supply characteristics and tank sizes; supports what we randomise. **Castelletti et al. 2013:** preference-conditioned RL gives a Pareto frontier in one run.
- **Method citations to use:** PPO (Schulman 2017), DQN (Mnih 2015), Stable-Baselines3 (Raffin 2021, JMLR 22), EPANET (Rossman 2000), WNTR (Klise et al.), cross-entropy method (de Boer et al. 2005), domain randomisation (Tobin 2017; general idea only).
- **Statistics references:** Henderson et al. 2018, Agarwal et al. 2021 (bootstrap CIs and interquartile mean for 3-10 runs), Colas et al. 2018: with 5 or fewer seeds, report interval estimates and be conservative.
- **Forward-citation search was NOT done** (no Google Scholar "Cited by"). "We did not find" is the only allowed wording.
