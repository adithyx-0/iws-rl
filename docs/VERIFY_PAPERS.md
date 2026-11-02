# Paper verification plan (split between Adithya and Adithyan)

**Why:** most sources in `docs/reference/iws-rl-literature-audit.md` were checked by an AI web search, and many only as abstracts or snippets. Before we present, a human must open each paper and confirm the specific facts we rely on. Until then, say only "to our knowledge, based on a targeted search".

**Time guide:** P1 papers first (they affect the novelty claim or a number on a slide), then P2, then P3 if time allows. About 15-20 minutes per P1 paper.

## Rules (keep it simple)
1. **Open the real page** (link or DOI). Do not ask an AI to summarise it for you; if you use one, still find the sentence in the paper yourself.
2. For each paper, answer the checklist, and **write the page or section number** next to each fact.
3. Mark one status: `FULL` (you read the relevant parts), `ABSTRACT` (only the abstract), `NOT FOUND`, or `WRONG` (citation or claim in our docs is wrong).
4. If the paper contradicts something we wrote, write it down plainly. That is a useful result.
5. Links marked *(from memory, confirm)* are not from the audit; check they open the right paper. If a link fails, search the title.
6. **Where to write:** copy the template at the bottom into your own file, `docs/verify/results_ADITHYA.md` or `docs/verify/results_ADITHYAN.md`, so you never edit the same file (no git conflicts). Push to your own branch and tell Adithya.

---

# PART A: Adithya (water, intermittent supply, equity; the closest prior work and our assumptions)

### A1 [P1] Holgado-Sánchez, Arias, Billhardt & Ossowski (2024). Algorithms for learning value-aligned policies considering admissibility relaxation. arXiv:2406.04838
Link: https://arxiv.org/abs/2406.04838
Why it matters: the audit says it may be constrained RL for equity in water distribution (a drought). If so, it is the biggest threat to our novelty claim. Only the abstract was read.
Verify and collect:
- [ ] Is the environment a **pipe network** (hydraulics, valves) or an abstract allocation problem?
- [ ] Does it involve **intermittent supply**, **zones**, or **household storage**? (yes/no each)
- [ ] Which RL algorithm and which **equity** measure? Is the equity a constraint (Lagrangian, RCPO) or a reward term?
- [ ] Any comparison against an **optimised fixed schedule**? Any **distribution-shift** tests?
- [ ] One sentence: how does it differ from ours?

### A2 [P1] Wanjiru, Zhang & Xia (2016). Model predictive control strategy of energy-water management in urban households. Applied Energy, 179, 821-831
Link: https://doi.org/10.1016/j.apenergy.2016.07.050
Why: the audit says it already reports "open-loop is fine for steady demand, closed-loop is more robust when demand changes" for rooftop tanks. That is the idea behind our regime finding. Only the abstract was read.
- [ ] Find the **exact sentence(s)** stating the open-loop vs closed-loop conclusion (page number).
- [ ] What demand change or disturbance was tested, and how large?
- [ ] Is it one household? What is the cost (energy, water)? Is there any equity or network?
- [ ] How should we cite it on a slide: "consistent with earlier open-loop vs closed-loop findings for household tanks" (is that accurate?)

### A3 [P1] Hendrickson & Sela (2024). Optimizing equity in intermittent water supply systems: A volume-driven demand and flow control approach. Sustainable Cities and Society, 112, 105615
Link: https://doi.org/10.1016/j.scs.2024.105615 (accepted manuscript: https://par.nsf.gov/servlets/purl/10536510)
Why: closest paper. The audit read it in full, but we will quote it, so confirm the facts ourselves.
- [ ] Confirm authors (two), year, volume 112, article 105615.
- [ ] Do they use **RL or any closed-loop control**? (audit says no)
- [ ] Their **tank-size robustness test**: perturbation size (audit: +-50%) and the conclusion (does the fixed schedule still beat no control?). Page number.
- [ ] How tanks are modelled (**inside** the hydraulic model?). Ours sit outside EPANET, so note this difference.
- [ ] Equity metric definition, and the headline numbers for the medium network (audit: supply ratio 0.79 to 0.87, equity 0.61 to 0.78).
- [ ] Number of zones/valves and the optimiser (audit: Bayesian optimisation, 100 iterations).

### A4 [P1] Hendrickson, Abhijith & Sela (2024). Volume-driven and flow control approach to optimizing equity in intermittent water supply systems. Engineering Proceedings, 69(1), 75
Link: https://doi.org/10.3390/engproc2024069075
- [ ] Confirm this is the conference version of A3, with **three** authors, and that 69/1/75 is its correct number.
- [ ] Note any difference from the journal version we would cite.

### A5 [P1] Kurian, Mohandoss, Chandrakesa, Chinnusamy, Narasimhan & Narasimhan (2023). Equitable supply in intermittently operated rural water networks in emerging economies. Water Supply, 23(11), 4520-4538
Link: https://doi.org/10.2166/ws.2023.268
Audit: only the abstract was read (publisher blocked). Try institutional access, the IIT Madras repository, or ask a librarian.
- [ ] Is the formulation **MINLP** or **MILP**? (the audit saw both)
- [ ] Are **household tanks** modelled? Is it a daily open-loop schedule? Any RL or closed-loop part?
- [ ] The data-driven variant: what does it use (flow/level measurements) and is it adaptive?
- [ ] Equity measure and the objective.

### A6 [P2] Kurian, Narasimhan & Narasimhan (2024). Analysis of inequity in rural water supply schemes: a case study from Central India. Engineering Proceedings, 69(1), 184
Link: https://doi.org/10.3390/engproc2024069184
- [ ] Confirm this is the paper behind "69/1/184" (not Hendrickson). Note anything useful on inequity under intermittent operation (head-end villages over-withdrawing).

### A7 [P2] Solgi, Bozorg Haddad, Seifollahi-Aghmiuni & Loaiciga (2015). Intermittent operation of water distribution networks considering equanimity and justice principles. J. Pipeline Systems Eng. Pract., 6(4), 04015004
Link: https://doi.org/10.1061/(ASCE)PS.1949-1204.0000198
- [ ] Equity-aware scheduling with a metaheuristic: confirm it is **not RL**, and how equity is defined.

### A8 [P2] Gullotta, Butler, Campisano, Creaco, Farmani & Modica (2021). Optimal location of valves to improve equity in intermittent water distribution systems. J. Water Resour. Plann. Manage., 147(5), 04021016
Link: https://doi.org/10.1061/(ASCE)WR.1943-5452.0001370
- [ ] Equity + valves + private tanks, no RL? Confirm. Note the equity metric.

### A9 [P2] Ayyash, Zhang, Javadi & Farmani (2024). Optimal operation of intermittent water supply systems under water scarcity. J. Water Resour. Plann. Manage., 150(3), 04024001
Link: https://doi.org/10.1061/JWRMD5.WRENG-6227
- [ ] Equity operation under **scarcity** (relevant to our scarce condition). Optimisation method? Any RL? Any tank model?

### A10 [P2] Papers seen only as snippets in the audit (open each; one line per paper)
- Pentyala, "CORE" adaptive pump thresholds for household tanks under intermittent supply (engrXiv preprint). Find the link by searching the title. **Adaptive control, so it may be close to us.** Is it RL? Closed-loop? Any equity?
- Ansalone & Chatzigiannakis (2025), RL for tariff-aligned filling of household storage tanks, IFIP Networking 2025: https://dl.ifip.org/db/conf/networking/networking2025/1571132384.pdf . RL on household tanks. Does it involve intermittent supply, valves or equity?
- Ramani et al. (2023), NSGA-II equity design of intermittent networks, Water. Find the link by searching.
- Ameyaw et al. (2013), multi-objective equity optimisation with consumer tanks, AQUA. Find the link by searching.

### A11 [P1] Sources for our ASSUMPTIONS (not searched yet; our parameters are currently uncited)
Collect **one citable number with a page reference** for each, or write "no source found":
- [ ] **Household roof-tank size** relative to daily use (we use 0.3-0.8 days of consumption). Search: "household storage tank capacity intermittent water supply", "roof tank volume India household survey". Possible leads: IWA specialist group on intermittent supply, Vairavamoorthy, Criminisi, Taylor et al., Klingel, Charalambous.
- [ ] **Demand surge when supply resumes** (our alpha = 4, tested 2 and 8). Search: "peaking factor intermittent supply", "peak demand after supply restoration".
- [ ] **Minimum service pressure** (we test 10, 20, 30 m). Search: "minimum pressure for service intermittent supply 10 m", WNTR pressure-driven demand documentation.
- [ ] **Daily supply hours / supply as a fraction of demand** (we use 50-90% of daily demand). Search: "hours of supply per day intermittent water cities".
- [ ] Note which of these is a cited range and which stays an assumption we must disclose.

---

# PART B: Adithyan (RL papers, methods, evaluation)

### B1 [P1] Siddique, Weng & Zimmer (2020). Learning fair policies in multi-objective (deep) reinforcement learning with average and discounted rewards. ICML 2020, PMLR 119, 8905-8915
Link: https://proceedings.mlr.press/v119/siddique20a.html (arXiv: https://arxiv.org/pdf/2008.07773)
- [ ] What exactly is optimised (generalised Gini welfare over a vector of per-user returns)?
- [ ] Is our "lambda times minimum zone supply, added once per day" a different thing? (we must not call ours "fair RL in the Siddique sense")
- [ ] Any water or network application? (audit: no)

### B2 [P1] Hu, Gao & Zhong (2023). Multi-agent reinforcement learning framework for real-time scheduling of pump and valve in water distribution networks. Water Supply, 23(7), 2833-2846
Link: https://doi.org/10.2166/ws.2023.163
Audit: snippet only.
- [ ] Algorithm (MADDPG?), controls (pumps and valves), objective (energy and water-loss cost?), any **equity** term?
- [ ] Continuous supply or intermittent? Network used? Baselines (GA, PSO, DE?)
- [ ] Any shift or robustness test?

### B3 [P1] Real-time pump scheduling in water distribution networks using deep reinforcement learning. J. Water Resour. Plann. Manage., 151(6) (2025). Authors UNKNOWN to us.
Link: https://doi.org/10.1061/JWRMD5.WRENG-6476
- [ ] **Find the authors.** Confirm title, volume and issue.
- [ ] Algorithm (PPO?), and the claim about robustness to demand uncertainty vs robust optimisation. Exact wording and page.
- [ ] Is the comparison against a **tuned fixed schedule**? Any distribution-shift test?

### B4 [P1] Hajgato, Paal & Gyires-Toth (2020). Deep reinforcement learning for real-time optimization of pumps in water distribution systems. arXiv:2010.06460
Link: https://arxiv.org/abs/2010.06460
- [ ] The **demand randomisation** at each episode: how exactly (per-node multipliers, total scale), with numbers.
- [ ] Were the test scenarios drawn from the **same** distribution as training (no shift test)?
- [ ] Find the **published journal version** and venue, if any.

### B5 [P1] Salaorni et al. (2025). Gym4ReaL: A suite for benchmarking real-world reinforcement learning. arXiv:2507.00257
Link: https://arxiv.org/abs/2507.00257
- [ ] The water environment (WDSEnv): actions (pumps, binary combinations), reward, baselines (rule-based? any tuned schedule?).
- [ ] Demand profiles used in training (normal, stressful, extreme?). Is it intermittent supply? Any equity?

### B6 [P2] Hu, Cai, Zeng, Yan, Gong & Wang (2020). Deep reinforcement learning based valve scheduling for pollution isolation in water distribution network. Math. Biosci. Eng., 17(1), 105-121
Link: https://www.aimspress.com/article/id/4233
- [ ] RL valve scheduling for contamination isolation: no equity, not intermittent? Confirm. (The "Cai" in our old notes may come from here.)

### B7 [P2] Belfadil, Modesto & Martin (2024). Leveraging deep reinforcement learning for water distribution systems with large action spaces and uncertainties: DRL-EPANET for pressure control. J. Water Resour. Plann. Manage. (2024)
Link: search the title (volume, issue and DOI are UNVERIFIED). An earlier workshop version: https://mlanthology.org/neuripsw/2022/belfadil2022neuripsw-drlepanet
- [ ] **Find volume, issue, DOI.** RL valve/PRV control without equity? Confirm.

### B8 [P2] Val Ledesma (2022). Safe reinforcement learning control for water distribution networks. PhD thesis, Aalborg University
Link: https://doi.org/10.54337/aau495039631
- [ ] Safe RL for water networks (pressure constraints): constrained RL used? Any equity? (we must not claim "no constrained RL in water")

### B9 [P1] The two names we cannot trace (settle these)
- [ ] **"Cai et al. 2024 (NeurIPS), asymmetric actor-critic / teacher-student with privileged information"**: arXiv https://arxiv.org/abs/2412.00985 *(from our reference list; confirm it opens and is real)*. Authors, title, venue. This is a general RL paper, not water. Is it relevant to our privileged-information baseline?
- [ ] **"npj Clean Water" equity paper** (mentioned in an outside brief): search npj Clean Water for intermittent supply, equity, RL. If you cannot find it, we remove it. The audit found only an urban-drainage RL paper there: Huang et al. 2025, https://www.nature.com/articles/s41545-025-00512-z (confirm it is drainage, not water supply).

### B10 [P2] Method and tool citations (we use them, so we must cite them). For each, collect full citation and a working link
- [ ] **PPO**: Schulman et al. 2017, arXiv:1707.06347 *(from memory, confirm)*.
- [ ] **DQN**: Mnih et al. 2015, Nature 518 *(confirm link)*.
- [ ] **Stable-Baselines3**: Raffin et al. 2021, JMLR 22(268), https://github.com/DLR-RM/stable-baselines3 and the sb3-contrib package (RecurrentPPO).
- [ ] **EPANET** (Rossman, US EPA) and **WNTR** (US EPA; use the citation the WNTR docs recommend): https://github.com/USEPA/WNTR . Find the recommended citation in the WNTR docs.
- [ ] **Cross-entropy method**: Rubinstein (1999) or de Boer et al. (2005) tutorial. Find one citable version.
- [ ] **Domain randomisation**: Tobin et al. 2017, arXiv:1703.06907 *(from memory, confirm)*.
- [ ] **Evaluation methodology**: Henderson et al. 2018 "Deep Reinforcement Learning that Matters" (arXiv:1709.06560) and Agarwal et al. 2021 "Deep RL at the Edge of the Statistical Precipice" (arXiv:2108.13264) *(from memory, confirm)*. One sentence each on what they say about seeds, confidence intervals and weak baselines.

### B11 [P3] Optional: forward-citation search (finds newer work the AI could not see)
- [ ] On Google Scholar, open "Cited by" for Hendrickson & Sela 2024 and for Gym4ReaL. List any paper that uses **RL for intermittent supply or equity**. If you find one, tell Adithya immediately: it changes the novelty claim.

---

## Template for your results file
Copy into `docs/verify/results_ADITHYA.md` or `results_ADITHYAN.md`, one block per paper:
```
### A1 (or B1...) Short title
Status: FULL / ABSTRACT / NOT FOUND / WRONG
Link that worked:
Facts (with page or section):
- ...
Differs from ours in:
Contradicts our docs? (yes/no, what)
Safe wording for the slide:
```

## When you finish
1. Push your results file on your own branch and message Adithya.
2. Adithya merges the verified facts into `docs/understanding_source.md` and the PDF, and fixes any wrong citation.
3. Anything you could not open: list it at the top of your file under "NOT VERIFIED". Honest gaps are fine; guessed facts are not.
