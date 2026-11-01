# Assumptions and limitations (M3, T3.2)

Source of values: `iws_env.py`, `v2cfg.py`, `eval_all.py`. "Evidence" = what supports the number today. **Nothing here is calibrated to a real city.**

## 1. Parameters

| Parameter | Value in code | Evidence | Status |
|---|---|---|---|
| Network | EPANET Net3 (92 junctions, 59 with demand, 2 sources, 3 tanks) | Shipped with `wntr`; designed for continuous supply | Assumption: not a real IWS network |
| Zones | 4, k-means on coordinates | Design choice | Assumption |
| Episode | 3 days x 24 hourly decisions | Design choice (`five_days` condition tests 5) | Assumption |
| Demand scale (v2) | 8x base demand | Chosen so hydraulics bind (`hyd_probe.py`: fill 0.54-0.73, pressure 13-18 m). Rationale: supplying a day's volume in a few hours raises peak flow by ~24/hours of supply. | Our reasoning, not a citation |
| Household tank | 0.3-0.8 days of consumption (uniform per node) | None cited. | **Unsourced.** See section 2 |
| Initial tank fill | 20-60% of capacity | None | Unsourced |
| Surge factor alpha | 4 (tested 2 and 8) | None; alpha controls how fast a tank refills | Unsourced; results are sensitive to it |
| Daily source budget | 50-90% of daily consumption | None | Unsourced; scarce (30-50%) is degenerate |
| Pressure thresholds | required 20 m, minimum 2 m (tested 10 and 30) | EPANET PDD defaults-style values | Hydraulic effect only in v2 |
| Demand noise | 10% per node (tested 30%) | None | Assumption |
| Diurnal pattern | 24-value fixed multiplier | None cited | Assumption |
| Reward lambda | 1.0 (equity term) | Tuning only | Swept by M2 (lam 0-4) |

## 2. Household tank size: what we found (searched 2026-11-01)
- No measured per-household tank-capacity survey was found by the search; the results were vendor guides and design norms.
- Design norm: India often uses about 135 litres/person/day. A Hubli-Dharwad study (*Water Resources Research*, 2017, "Measuring household consumption and waste in unmetered, intermittent piped water systems") found very few households actually use 135 L/person/day. [ABSTRACT/SNIPPET ONLY]
- Vendor sizing guidance (Sintex, Trubore): roughly 500-2000 L for a household; recommended backup 2+ days for irregular supply. Vendor advice, not survey data.
- Implication: our 0.3-0.8 days is probably BELOW typical installed storage (roughly 2 days by vendor advice). Sump + overhead tanks may explain part of that, but we have no source. Larger tanks make supply timing matter less (see `large_tanks` condition). **Say this on the limitations slide; do not defend 0.3-0.8 as realistic.**
- TODO: read the Hubli-Dharwad paper and the CSE Chennai household survey for measured numbers; if found, replace the range and re-run the `small_tanks` / `large_tanks` conditions.

## 3. Modelling limitations
1. Zone closure = consumers cut off; mains stay pressurised. No physical valve on a main, no pipe filling/draining (EPANET cannot do transients or filling).
2. One steady-state EPANET snapshot per hour; no pumping dynamics inside the hour.
3. Households aggregated at the junction, one tank per node, no pumps/sumps, no bottled/tanker water, no illegal tapping or leakage.
4. Source budget is a daily volume cap announced one day ahead; real sources are not like that.
5. Demand is fully served when tank water exists; no behavioural response to supply (hoarding, longer tank sizes).
6. Single network, one zoning (`zone_seed=0`); no evidence it transfers to other networks.
7. Simulation only; nothing is validated on field data.

## 4. Evaluation limitations (affect what we can claim)
- v1 environment was saturated: mean supply is capped near 0.773 by water volume, so v1 mean-supply comparisons say little (see `docs/reference/improvements_for_ref.md` section 2).
- Scarce condition: every method scores 0.44-0.47 (capped by total water). Judge only worst-zone / fairness there.
- The clairvoyant oracle sees future budgets and tank levels; it is an upper bound, not an achievable policy. Gate 1 failed on the plan's thresholds (+0.013 mean, +0.019 worst-zone).
- `ce_schedule` is cross-entropy search, not Bayesian optimisation, and stopped while still improving; M2 is rerunning it (3 seeds).
- PPO vs the optimised fixed schedule is within ~0.01 mean supply and PPO is slightly worse on worst-zone (v2). No claim of "RL beats optimised scheduling" is supported.
- `paired_vs_greedy.csv` compares against `greedy_k1`, the weakest strong baseline; compare against `ce_schedule` instead.
- Test seeds are 10000+ (100 scenarios default, 50 other conditions). Oracle: 30 scenarios.
- Bootstrap CIs are over scenarios; seed-to-seed spread is reported separately (`*_seed_sd`).
- Models were trained for different step counts in different places (150k v1, 300k v2, 500k long): always report the count.
