# Paper verification results: Part B (Adithyan)

Date: 2026-11-02. Plan: `docs/VERIFY_PAPERS.md` (on `main`).

**Method and limits (read first).** These checks were done with an AI-assisted web fetch/search of publisher, arXiv, DOI and
index pages. No full text was read and **no page numbers were found**. So nothing here is `FULL`. Status is at best `ABSTRACT`
(bibliographic data confirmed, abstract-level content). A human still has to open the papers and find the sentences for the
checklist items marked "OPEN". Several publisher pages (MDPI, ASCE, IWA) returned 403, so those were checked only via search snippets.

## NOT VERIFIED (honest gaps)
- B3: authors and abstract of JWRMD5.WRENG-6476 (ASCE page blocked, 403).
- B5: whether Gym4ReaL contains a water-distribution environment (not in the abstract).
- B10: DQN (Nature 518), Stable-Baselines3 (JMLR 22(268)), EPANET, cross-entropy method: not checked.
- B11: forward-citation search (Google Scholar "Cited by") not done; needs a person.
- B9: the "npj Clean Water" equity paper and the Huang 2025 drainage paper: not found by search.

---

### B1 Siddique, Weng & Zimmer (2020), ICML 2020, PMLR 119, 8905-8915
Status: ABSTRACT
Link that worked: https://proceedings.mlr.press/v119/siddique20a.html ; https://arxiv.org/abs/2008.07773
Facts: authors and venue/pages match the plan. arXiv title spells "Multiobjective" (no hyphen); PMLR spells "Multi-Objective".
The PMLR page abstract says only that an objective "which encodes a notion of fairness that we formally define" is optimised.
It does **not** name the welfare function on that page.
Differs from ours in: OPEN. Our `docs/related_work.md` says "generalised Gini welfare"; this was NOT confirmed on the page I fetched. A person must confirm in the paper body (section defining the fairness objective).
Contradicts our docs? Not shown. The "generalised Gini" wording stays unconfirmed.
Safe wording for the slide: "Siddique et al. (ICML 2020) study fair policies in multi-objective deep RL; our fairness term is a reward bonus on per-day zone supply, a different construction."

### B2 Hu, Gao & Zhong (2023), Water Supply 23(7), 2833-2846
Status: ABSTRACT (via search snippet of the abstract; publisher page 403)
Link: https://doi.org/10.2166/ws.2023.163 (redirects to iwaponline.com)
Facts: authors Shiyuan Hu, Jinliang Gao, Dan Zhong. MDP formulation, MADDPG for a fully cooperative multi-agent task, compared with GA, PSO and DE. Findings: water loss dominates scheduling; solution depends mainly on demand pattern, not tariff. Real-time solution faster than GA/PSO/DE.
Equity term: none in the abstract. Intermittent supply: not mentioned. Distribution-shift test: not mentioned. Network used: OPEN.
Note: an index lists arXiv 2408.08442 under this same title; use the DOI.
Contradicts our docs? No.
Safe wording: "RL (MADDPG) for pump and valve scheduling in continuous supply, aimed at energy and water loss; no equity objective in the abstract."

### B3 Real-time pump scheduling using DRL, JWRPM 151(6) (2025), doi 10.1061/JWRMD5.WRENG-6476
Status: NOT FOUND (ASCE page returned 403)
Authors: still unknown. Title, volume/issue, algorithm, robustness claim: OPEN. Do not cite until a person opens the page.

### B4 Hajgato, Paal & Gyires-Toth (2020), arXiv:2010.06460
Status: ABSTRACT
Link that worked: https://arxiv.org/abs/2010.06460
Facts: title "Deep Reinforcement Learning for Real-Time Optimization of Pumps in Water Distribution Systems". Published version: **J. Water Resour. Plann. Manage., vol. 146, issue 11 (Nov 2020)**, related DOI 10.1061/(ASCE)WR.1943-5452.0001287 (from the arXiv page journal-ref). Method: dueling DQN sets pump speeds from nodal pressures, two networks, baselines Nelder-Mead and differential evolution, efficiency above 0.98 vs best baseline, about 2x faster.
OPEN: exact demand randomisation per episode and whether test scenarios share the training distribution (not in the abstract; read the paper body).
Safe wording: "DRL pump control (dueling DQN) compared with Nelder-Mead and differential evolution; JWRPM 2020."

### B5 Salaorni et al. (2025), Gym4ReaL, arXiv:2507.00257
Status: ABSTRACT
Facts: 12 authors, submitted 30 June 2025. Abstract: suite of realistic environments for large state-action spaces, non-stationarity, partial observability; finds standard RL stays competitive with rule-based benchmarks.
The abstract does **not** mention water distribution. OPEN: whether a water environment (WDSEnv), its actions, reward and baselines exist; read the full PDF.
Safe wording: do not mention its water environment until confirmed.

### B6 Hu, Cai, Zeng, Yan, Gong & Wang (2020), Math. Biosci. Eng. 17(1), 105-121
Status: ABSTRACT (title, authors, journal, volume/issue/pages, DOI confirmed on the AIMS page)
Link that worked: http://www.aimspress.com/article/10.3934/mbe.2020006 ; DOI 10.3934/mbe.2020006
OPEN: confirm "no equity, not intermittent" from the abstract/body; not confirmed here beyond the title (pollution isolation).

### B7 DRL-EPANET (Belfadil et al.)
Status: ABSTRACT (via search aggregator listing, not the publisher page)
Facts: journal version **J. Water Resour. Plann. Manage., vol. 150, issue 2, Feb 2024**, DOI **10.1061/JWRMD5.WRENG-6108**. Title: "Leveraging Deep Reinforcement Learning for Water Distribution Systems with Large Action Spaces and Uncertainties: DRL-EPANET for Pressure Control". Authors listed: Anas Belfadil, David Modesto, Jordi Meseguer, Bernat Joseph-Duran, David Saporta, Jose Antonio Martin Hernandez. BDQ and BDQF, 10 real networks, up to 26% mean-pressure improvement. Workshop version: NeurIPS 2022 (mlanthology.org/neuripsw/2022/belfadil2022neuripsw-drlepanet).
Pressure control; equity not mentioned. The author order and DOI should be re-checked on the ASCE page.
Contradicts our docs? The plan lists authors "Belfadil, Modesto & Martin"; the full author list is longer.

### B8 Val Ledesma (2022), PhD thesis, Aalborg University
Status: ABSTRACT-LEVEL ONLY (bibliographic)
Link that worked: https://vbn.aau.dk/en/publications/safe-reinforcement-learning-control-for-water-distribution-networ-3
Facts: author Jorge Val Ledesma, Aalborg University (Dept. of Electronic Systems), 2022, 215 pages, supervisors Rafal Wisniewski and Carsten Skovmose Kallesoe. Keywords: reinforcement learning, water infrastructures, safety. The page has no abstract.
OPEN: whether it uses constrained RL. Do not claim "no constrained RL in water" until read.

### B9 Unresolved names
- Cai et al. 2024: CONFIRMED. "Provable Partially Observable Reinforcement Learning with Privileged Information", Yang Cai, Xiangyu Liu, Argyris Oikonomou, Kaiqing Zhang, NeurIPS 2024, arXiv:2412.00985. General RL, not water. Relevance to our privileged-information baseline: OPEN (read body).
- "npj Clean Water" equity paper: **NOT FOUND** in the searches run. Recommend removing it from our materials unless someone produces a link.
- Huang 2025 (s41545-025-00512-z): not found by search; "drainage, not supply" unconfirmed.

### B10 Method and tool citations
- PPO: CONFIRMED. Schulman, Wolski, Dhariwal, Radford, Klimov, "Proximal Policy Optimization Algorithms", arXiv:1707.06347 (2017).
- Domain randomisation: CONFIRMED. Tobin, Fong, Ray, Schneider, Zaremba, Abbeel (2017), arXiv:1703.06907.
- Henderson et al.: CONFIRMED. "Deep Reinforcement Learning that Matters", Henderson, Islam, Bachman, Pineau, Precup, Meger, AAAI 2018, arXiv:1709.06560. One-sentence content note: OPEN.
- Agarwal et al.: CONFIRMED. "Deep Reinforcement Learning at the Edge of the Statistical Precipice", Agarwal, Schwarzer, Castro, Courville, Bellemare, arXiv:2108.13264; the arXiv page notes a NeurIPS 2021 Outstanding Paper Award. One-sentence content note: OPEN.
- WNTR: per the PyPI snapshot (v0.4.0), cite Klise, Murray & Haxton (2018), "An overview of the Water Network Tool for Resilience (WNTR)", Proc. 1st International WDSA/CCWI Joint Conference, Kingston, Ontario, July 23-25, paper 075. Alternative: Klise et al. (2020) WNTR User Manual v0.2.3, EPA/600/R-20/185. Newer WNTR releases may recommend a different citation: check the current GitHub README.
- DQN, SB3, EPANET, cross-entropy: NOT VERIFIED.

### B11 Forward-citation search
NOT DONE. Needs Google Scholar "Cited by" on Hendrickson & Sela 2024 and Gym4ReaL. If anything uses RL for intermittent supply or equity, tell Adithya immediately.

---
## Incidental checks for Part A / `docs/related_work.md` (not my assigned part)
- Kurian et al. 2023, Water Supply 23(11), 4520-4538: confirmed via search; authors Varghese Kurian, Prasanna Mohandoss, Srinesh Chandrakesa, Saravanan Chinnusamy, Shankar Narasimhan, Sridharakumar Narasimhan. Abstract: MINLP, plus a data-driven version using flow and level measurements. `related_work.md` lists no authors for it; add them.
- Hendrickson & Sela: MDPI conference version title is "Volume-Driven and Flow Control Approach to Optimizing Equity in Intermittent Water Supply Systems", Eng. Proc. 69/1/75. Journal version: Sustainable Cities and Society 112 (2024), doi 10.1016/j.scs.2024.105615 (from search). Author lists not confirmed by me.
- MDPI 69/1/184 (Kurian, Narasimhan & Narasimhan): page returned 403; the earlier search listing was consistent with the plan.
