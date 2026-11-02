# Verification results: Part A (Adithya)

Version 2, 2026-11-02. IMPORTANT: this was done by an AI (Claude) reading the pages and the PDFs you supplied, not by a human. Per our own rule, a human should still find the sentence for every fact that ends up on a slide. Page numbers below are the journal page footers (A2, A5) or manuscript page numbers (A9); for the others I used section numbers. Items marked CHECK need a human.

Status summary
- FULL: A1, A2, A3, A4, A5, A6, A7, A9, A10-Ansalone
- ABSTRACT: A8 (Gullotta valves paper, still no PDF), A10-CORE, A10-Ramani, A10-Ameyaw
- WRONG (small corrections): A10-Ansalone (title and author list differ from our paraphrase)

---

### A1 Holgado-Sanchez et al. 2024, value-aligned policies, admissibility relaxation
Status: FULL (arXiv v1 full text; venue not verified)
Link that worked: https://arxiv.org/abs/2406.04838 (PDF: https://arxiv.org/pdf/2406.04838v1)
Facts (section numbers):
- Authors/title match: Andres Holgado-Sanchez, Joaquin Arias, Holger Billhardt, Sascha Ossowski; submitted 2024-06-07 (cs.AI).
- Environment is NOT a pipe network. A tanker truck (capacity 60,000 L) moves between a reservoir and 4 villages on a road network, dispensing water (Sec 4, Fig 1). No hydraulics, valves, zones or household tanks. State = litres per inhabitant per village, truck position and load (Sec 4.2); village consumption rises with its reserve (Sec 4.1).
- Yes/no list: intermittent supply no; zones no; household storage no (village-level reserve only).
- Algorithm: tabular Double Q-learning with average-reward objective (Sec 5): eps-ADQL (Alg 1, based on CDQL safe-action sets) and eps-CADQL (Alg 2, adds an RCPO-style Lagrangian penalty, Sec 5.2).
- Equity measure: f_gini = 1 - Gini index of water per person (Sec 4.3), used as the per-step reward (Sec 5), so equity is a reward term. In eps-CADQL a per-state threshold tau = 0.7 is enforced as a constraint via the Lagrangian (Sec 5.2); eps-local restricts actions to near-greedy-equity ones (Def 6).
- Comparisons: against a greedy "local" policy and plain ADQL, not an optimised fixed schedule (Sec 6.2). Path-average equity about 0.84 (eps-ADQL) vs 0.71 (local) (Sec 6.2).
- Shift tests: none on demand or environment. Closest: policies trained at eps = 0.1 evaluated at eps = 0.01 without retraining, and 1000 random initial states (0-600 L per village) (Sec 6.2, Fig 4-5).
- Setup: 30,000 iterations, alpha 0.03, tau 0.7, 5 hidden levels (Sec 6.1).
Differs from ours in: abstract truck allocation vs hydraulic network with zonal valves and household tanks; tabular Q-learning; no intermittent supply or tanks; no fixed-schedule baseline; no regime analysis.
Contradicts our docs? Partly. It IS constrained RL for EQUITY in a drought water-distribution problem (Lagrangian/RCPO style). So do NOT write "no constrained RL for equity in water". It is not a pipe-network or intermittent-supply paper, so a narrowly worded novelty claim survives.
Safe wording for the slide: "To our knowledge, prior RL work on equitable water allocation under drought (Holgado-Sanchez et al., 2024) uses a tanker-truck allocation abstraction with tabular Q-learning, not a hydraulic network with zonal valves and household tanks under intermittent supply."
CHECK: whether a later published version exists and its venue.

### A2 Wanjiru, Zhang, Xia 2016, MPC energy-water management in urban households
Status: FULL (your PDF)
Link that worked: https://doi.org/10.1016/j.apenergy.2016.07.050 (postprint also at https://repository.up.ac.za/handle/2263/57390)
Facts (journal pages):
- Citation confirmed: Applied Energy 179 (2016) 821-831; received 29 Mar 2016, accepted 14 Jul 2016, online 22 Jul 2016.
- It is ONE house: a five-occupant maisonette in Tshwane, South Africa (Sec 3.1, p. 826). Tank: 1000 L cylindrical, 1.1 m diameter, 1.3 m height, usable levels 0.12-1 m. Pump: fixed speed, 0.8 kW, 0.9 m3/h. Demand measured hourly for one week with a flow meter (Fig 2).
- NOT an intermittent-supply study. It assumes municipal water is always flowing at low pressure with no rationing (Sec 2.2, p. 823); it says the formulation could handle rationing if supply times are known, but does not test it (Sec 2.2, Sec 4.3).
- Objective (Eq 8, p. 824): weighted sum of time-of-use (TOU) electricity cost and a pump-switching count used as the maintenance cost, so both "pumping cost" and "maintenance cost" wording in the abstract refer to this one objective. 10-min sampling, 144 steps/day, binary on/off pump solved with SCIP (Sec 2.2, 2.3).
- Open-loop uses the predicted diurnal demand; closed-loop MPC uses tank-level sensor feedback and re-solves with a receding horizon (Sec 2.4, p. 825). MPC needs extra level sensors, which adds cost and complexity (Intro, p. 822).
- Exact conclusion (Abstract p. 821; Sec 4.3, p. 829): open-loop is suitable when only random disturbances from measurement errors are present; closed-loop MPC is suitable when the demand pattern changes (example: occupancy change); open-loop is cost-effective and easy to implement for steady demand patterns.
- Disturbances tested (Sec 4.2, pp. 827-829): (1) random error up to 50% of demand ("a very inaccurate system"): open-loop 0.84 R/day vs MPC 0.92 R/day, open-loop mostly stays within constraints and is cheaper. (2) Sudden demand spike of +70% between 18:00 and 20:00: open-loop does not react and the tank empties before the end of the day; MPC pumps 10 min at 20:10 and keeps water available, at 0.92 R/day vs 0.84.
- Table 1 (p. 830): baseline 1.63, open loop 0.84, MPC 0.84 (no disturbance) and 0.92 (random or spike) R/day. Savings vs baseline: 48.5% open loop, 43.6% MPC; MPC costs 9.5% more than open-loop (Sec 4.3, p. 829).
- Turnpike effect (Sec 4.2.3, Fig 7): open-loop end-of-day level need not match the start, so later days may fail; MPC corrects over days.
Differs from ours in: single household, energy cost under a TOU tariff, binary pump, no network, no equity, no intermittent supply.
Contradicts our docs? No. The audit's paraphrase is accurate. The nuance is that "open-loop is fine" holds for random noise, even at 50% error, but fails under a pattern change (+70% spike).
Safe wording for the slide: "Consistent with a single-household rooftop-tank study (Wanjiru et al., 2016), where open-loop pump schedules cope with random demand noise but fail under a demand pattern change, and closed-loop MPC avoids tank depletion at about 9.5% higher energy cost." Do not say it tested equity, networks or intermittent supply.

### A3 Hendrickson & Sela 2024, volume-driven demand and flow control (journal)
Status: FULL (publisher-format PDF from par.nsf.gov)
Link that worked: https://par.nsf.gov/servlets/purl/10536510
Facts (section numbers):
- Citation confirmed: Greg Hendrickson and Lina Sela (two authors); Sustainable Cities and Society, vol 112, article 105615; received 9 Mar 2024, accepted 18 Jun 2024, online 24 Jun 2024.
- No RL and no closed loop. Open-loop flow-control-valve (FCV) setting schedule found by Bayesian optimisation (Sec 2.4, Sec 3). They assume no tank-level sensing and a known/forecast supply schedule, with schedules recomputed per horizon (Sec 1, Sec 2.4). They argue sensor-based central control may be impractical in IWS because of telecoms (Sec 1, citing Creaco et al. 2019). NOTE: we must justify our closed-loop observation assumptions against this.
- Tank-size robustness (Sec 3.2.6): tank capacities randomised from -50% to +50% of the original; same optimised FCV schedule re-applied. Result: consistent improvement in SR and SE over the new no-control baselines. SR drops versus the original optimised case; SE improved in many cases. So yes, the fixed schedule still beats no control.
- Tank modelling (Sec 2.2, Fig 1): inside the hydraulic model. Each consumer node gets a check valve, a storage tank, and a downstream pressure-driven demand node (volume-driven demand). WNTR + EPANET 2.2, 24 h, 5-min step. Inlet closes at 99% full, reopens at 95%. Ours sit outside EPANET, a real difference.
- Tank size assumption: baseline tank capacity equals total daily demand (Sec 2.2). Ours is 0.3-0.8 days.
- Equity metric (Sec 2.3, Eq 1-3): SR_n^t = q/d. SE_t = 1 - (1/N) * sum_n |mean SR_t - SR_n^t| / mean SR_t; SE = time average; 1 = perfect. A mean-absolute-deviation uniformity index, not minimum-based or Gini.
- Medium network S-2 (Sec 3.2): modified KY24, branched, 161 consumers, 6 zones each behind an FCV plus transmission main Z-0, 6 settings per FCV (36 variables); pumps on for the first 8 h of 24. SR 0.79 to 0.87, SE 0.61 to 0.78 (+28%) (Sec 3.2.2, Sec 4.2). Audit numbers confirmed.
- Optimiser (Table 1): scikit-optimize gp_minimize, GP surrogate, Matern kernel, Expected Improvement, 100 iterations, 5 initial points, xi 0.01, alpha 0.1; about 10 min per run.
- Useful for our regime story: more distributed supply (same 8 h total) makes controls less effective (Sec 3.2.4); FCVs beat PRVs (Sec 3.2.5); intermittency worsens the supply hierarchy (Abstract, Sec 4.1). Limitations (Sec 4.3): 24 h horizon, pipes assumed full, no filling/draining.
Differs from ours in: open-loop BO schedule vs learned/closed-loop policy; tanks inside EPANET vs outside; tank = 1 day of demand vs 0.3-0.8; spread-based equity vs our min-zone-supply term.
Contradicts our docs? No. All audit facts check out.
Safe wording for the slide: "Closest prior work optimises an open-loop valve schedule for equity with household tanks inside the hydraulic model (Hendrickson & Sela, 2024); it uses Bayesian optimisation, no learning, and is robust to +-50% tank-size error."
CHECK: add journal page numbers when you open the PDF.

### A4 Hendrickson, Abhijith & Sela 2024, conference version
Status: FULL (MDPI open access, 4 pages)
Link that worked: https://www.mdpi.com/2673-4591/69/1/75 (DOI https://doi.org/10.3390/engproc2024069075)
Facts:
- Confirmed: Engineering Proceedings 2024, vol 69, issue 1, article 75; online 6 Sep 2024; three authors: Greg Hendrickson, Gopinathan R. Abhijith (IIT Kanpur), Lina Sela. Presented at WDSA/CCWI 2024, Ferrara, 1-4 July 2024.
- Same S-2 numbers: SR 0.79 to 0.87, SE 0.61 to 0.78 (Sec 3).
- Differences from the journal version (A3): no small system S-1, no supply-schedule scenarios, no PRV comparison, no tank-size sensitivity test, no BO settings.
Contradicts our docs? No.
Safe wording: cite A3 for the +-50% test and BO details; cite A4 only as the conference precursor.

### A5 Kurian et al. 2023, equitable supply in intermittently operated rural water networks
Status: FULL (your PDF)
Link that worked: https://doi.org/10.2166/ws.2023.268
Facts (journal pages 4520-4538):
- Citation confirmed: six authors (Kurian, Mohandoss, Chandrakesa, Chinnusamy, S. Narasimhan, S. Narasimhan), Water Supply vol 23 no 11, 4520; first received 8 Jun 2023, accepted 28 Sep 2023, online 13 Oct 2023; CC BY-NC-ND.
- MINLP vs MILP, resolved: the general scheduling problem P is a mixed integer non-linear program (hydraulics in the constraints) (Sec 2.3, p. 4525). Its tractable reformulation P1 is an integer program with linear constraints that "can be solved by standard solvers to obtain provably globally optimal solutions" (Sec 3.2, p. 4528; keywords say mixed integer linear programming). The audit saw both because both appear.
- Household tanks? No. Demand nodes are at community level (village or overhead-tank inlet), with "individual- or village-level storage" assumed sufficient so that water is withdrawn at the maximum rate whenever supply is on (Sec 2.1, pp. 4523-4524). There is no tank-level state in the model. Source head is assumed constant; ON/OFF valves only; network assumed leak-free and pressurised.
- Open-loop daily schedule? Yes. The scheduler is solved every day, outputs which valve state is active in each interval (Fig 4, Fig 5, p. 4528-4529). The pump on/off in the lab was a LabVIEW level rule for the source tank, but the schedule itself has no feedback. No RL.
- Data-driven variant (Sec 3.3, p. 4529): replaces the hydraulic model with measured steady-state flow rates into each village for each of the 2^n valve states (64 states for 6 valves), stored in a lookup table; "a one-time exercise that is not repeated" (Conclusion, p. 4536). In the lab each state ran for 3 min and the flow was computed from tank-level change (Sec 4.2.2, p. 4533). It is not adaptive. The authors note the data requirement grows with the number of demand nodes and propose using a subset of "efficient" states (Sec 5, p. 4535).
- Equity measure and objective (Eq 6, Eq 12; Sec 2.2-2.3): z_i = (volume supplied to village i / demand d_i) - 1, the relative deviation of supply from demand. Objective: minimise ||z||_p, in the case studies the maximum relative deviation (p. 4525, p. 4530). It combines demand satisfaction and uniformity in one expression (Sec 1.2, p. 4522).
- Constraints: at most one valve operation per operator per interval, a cap on valve switches (n_is = 4, i.e. at most two ON switches), and allowed supply windows (Eq 7-10, 16-18).
- Results: Osmanabad model (6 villages, 64 states, 10 h horizon in 24 intervals, EPANET with nodes modelled as OHT inlets): relative deviation 4.0-5.6% (Scenario 1), 5.5-14.8% when village 5's valve is always open (Scenario 2) (pp. 4529-4531). Lab network (one 100 L overhead tank, six 25 L small tanks, 3000 s in 24 intervals of 125 s): maximum predicted deviation 1.5% (T4), minor differences between predicted and achieved supply over 3 repetitions (p. 4533). Solve times seconds to under 5 min with CPLEX on NEOS (p. 4529).
Differs from ours in: village/overhead-tank scale, no storage dynamics, ON/OFF valves, daily open-loop MILP, no demand shift analysis, no RL.
Contradicts our docs? Only the MINLP/MILP point, now explained.
Safe wording: "equity-oriented daily valve scheduling for intermittently operated rural schemes, formulated as a MINLP and solved as an integer program, with a measurement-based variant (Kurian et al., 2023); village-level demand nodes, no household tank dynamics, no learning."
Correction to my v1 note: the related Adhityan, Kurian & Narasimhan "Data driven approach for equitable supply in water networks" paper is from the 2nd WDSA/CCWI conference, Valencia, 18-22 July 2022 (this paper's reference list), not 2024.

### A6 Kurian, Narasimhan & Narasimhan 2024, inequity in rural water supply schemes, Central India
Status: FULL (MDPI open access, 4 pages)
Link that worked: https://www.mdpi.com/2673-4591/69/1/184
Facts:
- Confirmed this is the "69/1/184" paper and it is NOT Hendrickson: Varghese Kurian, Shankar Narasimhan, Sridharakumar Narasimhan (IIT Madras); Eng. Proc. 2024, 69(1), 184; published 9 Oct 2024.
- Network: 107 villages in Central India designed at 55 lpcd, two zones (A with 23 overhead tanks, B with 19), OHTs filled once a day by pumps, downstream by gravity (Sec 1).
- Key causes of inequity (Abstract, Sec 3.2): excess withdrawal by villages near the source, plus air locks. Table 1: village 1 draws 28.23 L/s under pressure-driven analysis vs 5.90 L/s demand-driven. Head-end over-withdrawal confirmed.
- Mitigations (Sec 3.2): booster pump (30 m head), isolating earlier villages; "no single solution fits all". Design principle: consumer pressure above 7 m.
- No RL, no household tanks.
Contradicts our docs? No.

### A7 Solgi et al. 2015, intermittent operation, equanimity and justice
Status: FULL (author-hosted copy of the published PDF at eScholarship)
Link that worked: https://escholarship.org/uc/item/3xb4j737
Facts (article pages 04015004-1 to -11):
- Confirmed: Solgi, Bozorg Haddad, Seifollahi-Aghmiuni, Loaiciga; J. Pipeline Syst. Eng. Pract., 6(4), 04015004; published online 13 Jan 2015 (listed 2015-11). Note: A5's reference list gives the year as 2014.
- Method: honey bee mating optimisation (HBMO), a metaheuristic, linked to EPANET. Not RL (p. 1-2).
- Equity definitions (p. 2, Eq 1-3): equanimity = same supply/demand ratio at all nodes; justice = each node's ratio at least theta times the network ratio R (theta = 0.9 in the case studies, p. 4). Objective (Eq 4): maximise mean pressure-supply index minus K2 times the coefficient of variation of R_i.
- Decision variable: on/off supply status of each node per interval (144 variables for the 6-node two-loop network, p. 4; 780 for the real Tehran network, p. 9).
- No consumer tanks modelled (only the supply reservoir, Eq 17-19).
- Case studies: two-loop network (6 nodes) and a Tehran network. Scarcity scenarios RW = 30%, 50%, 70% of demand (p. 4, Table 2).
Contradicts our docs? No.
Safe wording: "metaheuristic (HBMO) intermittent-supply scheduling with node-level equity constraints, no household tanks and no learning (Solgi et al., 2015)".

### A8 Gullotta et al. 2021, optimal location of valves (JWRPM)
Status: ABSTRACT (ASCE blocked; no PDF supplied). Secondhand detail from a follow-up paper by the same authors that I read in full (Gullotta, Campisano, Creaco, Modica 2021, Water Resour. Manage. 35:4477-4494, https://doi.org/10.1007/s11269-021-02962-9).
Link that worked: abstract via https://www.iris.unict.it/handle/20.500.11769/527934
Facts:
- Bibliographic data confirmed by the reference lists of A3, A5 and A9: Gullotta, Butler, Campisano, Creaco, Farmani, Modica; JWRPM 147(5), 04021016.
- Abstract: methodology to improve equity in intermittent networks with users equipped with PRIVATE TANKS; finds optimal valve locations and settings; two NSGA-II schemes (closed gate valves; control valves with settings); EPA-SWMM pressure-driven simulation; case study in northern Italy under water shortage; a few valves raise global equity.
- Per A9's introduction (read in full), the first scheme places fully closed valves and the second optimises location and setting of control valves, with UC as the equity metric. So equity + valves + private tanks, no RL: confirmed at abstract level. Valves have fixed settings, not time-varying schedules.
- From the follow-up paper (Sec 2.1, Sec 3): same network; equity uses UC = 1 - ADEV/ASR; tanks are "equivalent tanks" per node at 250 L per person; 25 demand nodes; 70% of demand supplied continuously for 24 h.
CHECK (needs the A8 PDF): the equity metric and tank sizing in A8 itself.

### A9 Ayyash et al. 2024, optimal operation of IWS under water scarcity
Status: FULL (your accepted-manuscript PDF)
Link that worked: https://ore.exeter.ac.uk/repository/handle/10871/134783
Facts (manuscript page numbers):
- Confirmed: Faten Ayyash, Chao Zhang, Akbar A. Javadi, Raziyeh Farmani; J. Water Resour. Plann. Manage., 150(3), 04024001; published 8 Jan 2024.
- Method (pp. 7-12): two steps. (1) Sectorise the network using modularity clustering in Gephi plus bridge-pipe selection (connectedness, direct source access, minimum cut). (2) NSGA-II (Platypus) with EPyT/EPANET 2.2 pressure-driven simulation, three objectives: pumping cost, equity, level of pressure. Not RL.
- Pressure-driven demand (Wagner) with pm = 0 m, preq = 15 m, exponent 0.5 (p. 10). Pressure reference for the pressure objective Pref = 20 m, taken from the Battle of Intermittent Water Supply instructions (p. 12). Citable for our 10/20/30 m grid.
- Equity metric (p. 11, Eq 4): UC_min = min over hours of [1 - ADEV/ASR], i.e. maximise the worst hourly Gottipati-Nanduri uniformity coefficient. A min-over-time objective, though still spread-based across consumers.
- Scarcity (p. 13): D-Town benchmark (399 nodes, 443 pipes, 11 pumps, 5 PRVs, 7 tanks, one reservoir); a flow-limiting valve caps supply at 220 L/s vs 264 L/s average demand, about 83% (my arithmetic). Five demand patterns, 24 h, 1 h step.
- Tanks: the 7 tanks are network/service tanks feeding sectors (Fig 2, Table 4); initial levels zero and end level equals start level (pp. 9-10, 12). Household tanks are NOT modelled; the authors say the presence of household tanks and the filling/emptying of pipes need further modelling work (Conclusions, p. 27). Household tanks appear only in the narrative explanation of results (p. 22).
- Decision variables (p. 13): 168 = tank trigger-on/off levels for pumps and valve V2, 24 hourly PRV settings, 120 hourly on/off values for 5 bridge pipes. So a day-ahead schedule plus simple level-based trigger rules.
- NSGA-II settings (p. 14): population 200, 200,000 evaluations, Pc 0.95, Pm 0.01, 15 independent runs; about 300 min.
- Results (pp. 15-26): existing min UC 0.30 at 20:00, $1083/day, LP 0.80. Non-sectorised optimum: $1060, min UC 0.49, LP 0.87. Sectorised optimum: $871, min UC 0.64, LP 0.90 (18% energy saving). Median node supply ratio 0.65 to 0.98 (Fig 10). Sector 3 stays poorly served (13.34 of 37.33 L/s, Table 5).
- Small inconsistency to be aware of: sector 3 average required demand is 37.77 L/s in Table 3 but 37.33 in Table 5.
Differs from ours in: no learning, no household tanks, multi-objective cost/equity/pressure, benchmark network, day-ahead schedule.
Contradicts our docs? No. This also confirms first-hand what A3 says about this paper ignoring consumer storage.
Safe wording: "NSGA-II sectorisation and operation under scarcity with equity, cost and pressure objectives (Ayyash et al., 2024); no household tanks and no learning".

### A10 Other papers
Pentyala et al. (CORE)
Status: ABSTRACT (engrXiv preprint page and intro snippets; the downloadable file was a .docx I could not parse)
Link: https://engrxiv.org/preprint/view/7798
- "CORE: Household-Learned Adaptive Thresholds for Pump Scheduling in Intermittent Water Supply Systems", Pentyala Samanvith Chowdary and co-authors (Keshav Memorial Institute of Technology), posted 3 Aug 2026, unreviewed preprint.
- NOT RL. Per-household, per-hour-of-day threshold from historical mean and standard deviation, re-estimated nightly. Tested on 100 households over 90 days (synthetic pySIMDEUM and real DAIAD Alicante data) against VTL and ASAR baselines. No equity, no network, no valves.
Ansalone et al. 2025
Status: FULL (your PDF, 6 pages; matches what I read earlier). WRONG in our wording: actual title is "A Reinforcement Learning Approach to Demand Balancing and Tariff Optimization in Blockchain-Based Smart Water Networks"; FOUR authors (Ansalone, Chatzigiannakis, Taormina, Garlisi); IFIP Networking 2025, Limassol, 26-30 May 2025.
Link: https://dl.ifip.org/db/conf/networking/networking2025/1571132384.pdf
- DQN (Sec III) selects one of three daily consumption patterns per user node, EPANET/WNTR in the loop; users have storage tanks; time-of-use tariffs (high 3:00-15:00 and 18:00-24:00); reward = beta * water cost + delta * penalty for unsatisfied demand, with beta = 100 and delta = 1000 (Eq 2, Sec IV). 23-node, 24-pipe benchmark; baselines uniform, random, mixed pattern assignment (Sec IV, p. 5). Continuous supply: no intermittent supply, no valves, no equity, no tuned fixed schedule, no shift test.
Ramani et al. 2023
Status: ABSTRACT plus intro text
- Ramani, Rudraswamy, Umamahesh, "Optimal Design of Intermittent Water Distribution Network Considering Network Resilience and Equity in Water Supply", Water 2023, 15(18), 3265, https://doi.org/10.3390/w15183265. NSGA-II for pipe-diameter DESIGN with resilience, uniformity coefficient and cost objectives, pressure-driven analysis, two benchmark networks. Not RL, not operation.
Ameyaw et al. 2013
Status: ABSTRACT
- Ameyaw, Memon, Bicik, J. Water Supply: Research and Technology - AQUA 62(8), 552-562, DOI 10.2166/aqua.2013.065. Multi-objective optimisation (GANetXL, EPANET2) of equity vs cost; intermittent systems modelled pressure-dependent through consumer storage tanks; decisions are location and sizing of source reservoirs. Not RL.

### A11 Sources for our assumptions
Tank size relative to daily use (we use 0.3-0.8 days): NO direct source for that range.
- Hendrickson & Sela 2024 baseline: tank = 1 day of demand, tested +-50% (Sec 2.2, 3.2.6).
- Gullotta et al. 2021 (follow-up paper), Sec 3: 250 L per person private tanks (not expressed in days).
- Wanjiru et al. 2016 (A2): one rooftop tank of 1000 L for a 5-person house; the text gives no daily total, only the hourly profile in Fig 2, so I cannot state it as a ratio.
- MacRorie et al. 2024, Eng. Proc. 69(1), 38 (Nepal, 56 smart meters), Sec 3: households split at 500 L storage (29 below, 27 at or above).
- Vendor guidance (1-2 days of storage; one site suggests a roof tank holds about half a day): weak, do not cite as evidence.
Status: assumption we must disclose; our range is below the literature default of 1 day.
Demand surge on supply resumption (alpha = 4, tested 2 and 8): NO primary source found.
- A course lecture note says hourly peak factors of 4-6 are adopted for intermittent systems (hufocw.org, weak).
- Meyer et al. 2023 (Sci. Total Environ. 892:164393) via India Water Portal summary: Bengaluru schedules induce peak flows of only 1.3 times average flow. City-wide supply-schedule peak, not a household surge. Original not opened.
- Wanjiru et al. 2016 (A2) tested demand disturbances of +70% for 2 h and random error up to 50% (Sec 4.2), which is about demand shifts, not post-outage surge.
Status: assumption we must disclose.
Minimum service pressure (we test 10, 20, 30 m): partly supported.
- Ayyash et al. 2024 (A9, pp. 10, 12): required pressure 15 m (pressure-driven demand) and 20 m reference pressure.
- Sanchez-Navarro et al., Water Supply, Nov 2021 (abstract, https://doaj.org/article/40f3ffd0a2e24a4aa0af233ffc1cdd40): 7-30 m of water column essential for user satisfaction; at least 6 h of service recommended.
- Kurian et al. 2024 (A6): design principle above 7 m. Solgi et al. 2015 (A7, p. 4): minimum pressure 30 m in the two-loop network and 14 m in the Tehran network.
- National-standards comparison (https://eprints.whiterose.ac.uk/id/eprint/120017/9/557.full.pdf; I did not capture its title or authors, open it to cite): 7 m guaranteed in England and Wales with internal company standards of 10-20 m; 10 m in Vietnam; about 24 m in South Africa.
- WNTR documentation not checked.
Status: 7-30 m range and 15/20 m reference values are citable; the exact 10/20/30 grid is our choice.
Daily supply hours and supply as a fraction of demand (we use 50-90%): partly supported.
- Hours: Delhi 4.3 h/day and Bengaluru 3.0 h/day population-weighted (Meyer et al. 2023 via India Water Portal summary); about 4 h/day average for Indian cities (Mohan and Abhijith article, secondhand); Lahan, Nepal: two 3-hour windows daily (MacRorie et al. 2024, Sec 2); A3 uses 8 h of 24; A5 uses a 10 h horizon (Sec 4.1).
- Fraction of demand: Solgi et al. 2015 at 30%, 50%, 70% (Table 2); Gullotta et al. 2021 at 70%; Ayyash et al. 2024 at about 83% (220 of 264 L/s, my arithmetic); Bengaluru production 106 LPCD vs the 135 LPCD guideline, about 79% (my arithmetic on a secondhand summary).
- No source found for the 90% upper end.
Status: 50-83% has support; 90% stays an assumption.

---
Cross-notes for Adithyan (Part B), found incidentally
- B4: Ansalone et al.'s reference list gives Hajgato, Paal, Gyires-Toth (2020) as J. Water Resour. Plann. Manage., 146(11), 04020079 (probably the journal version of arXiv:2010.06460; confirm).
- B2: the same list cites "Hu, Gao, Zhong, Wu, Liu (2023), Real-time scheduling of pumps in water distribution systems based on exploration-enhanced deep reinforcement learning, Systems 11(2), 56", a different Hu et al. paper from our B2 (Water Supply 23(7)); make sure they are not confused.

Papers surfaced that may be missing from the audit (check)
- Abdelazeem & Meyer 2024, JWRPM 150(1), 04023071 (modelling choices and inequality in IWS).
- Randeniya et al. 2022, Water Supply 22(5), 4781-4797 (equity vs performance trade-off in rationing with domestic storage), cited in A3.
- Nyahora et al. 2020, Water Supply 20(5), 1592-1603; Ilaya-Ayza et al. 2017 (equity optimisation); Solgi et al. 2020, Water Supply 20(7), 2630-2647 (multi-objective intermittent operation), cited in A9.
