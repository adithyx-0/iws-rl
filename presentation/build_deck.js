// Builds presentation/IWS_RL_deck.pptx from the content in presentation/PPT_CONTENT.md.
// Run: NODE_PATH=<folder with node_modules/pptxgenjs> node presentation/build_deck.js
// Numbers come from results_v2/ (see PPT_CONTENT.md). Edit text here, rerun, done.
const path = require("path");
const pptxgen = require("pptxgenjs");
const SK = "C:/Users/adith.ADITHYAN/.claude/skills/synced/dddcc719-6a80-4e34-9b09-d3bf39978020_dc6fc5bc-fb37-4892-8ea3-9d19ed0a5229/pptx";
const { applyTheme } = require(SK + "/scripts/apply_theme.js");

const ROOT = path.resolve(__dirname, "..");
const IMG = (f) => path.join(ROOT, "plots", "out", f);
const OUT = path.join(__dirname, "IWS_RL_deck.pptx");

const THEME = {
  name: "IWS Water",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0F2A33", lt1: "FFFFFF", dk2: "2A3A42", lt2: "F4F7F6",
    accent1: "17687A",   // teal: RL / main accent
    accent2: "B85A0B",   // orange: the tuned fixed schedule (the baseline to beat)
    accent3: "5B6B73",   // muted grey
    accent4: "7CC4D4",   // light teal (on dark)
    accent5: "D5DEDB",   // light line
    accent6: "3F8F5F",
    hlink: "17687A", folHlink: "5B6B73",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";            // 13.333 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Can reinforcement learning share scarce water fairly?";
pres.author = "Adithyan";
const C = pres.SchemeColor;
const W = 13.333, M = 0.6, CW = W - 2 * M;   // margins and content width

// ---------- layouts ----------
pres.defineSlideMaster({ title: "TITLE", background: { color: C.text1 }, objects: [] });
pres.defineSlideMaster({
  title: "CONTENT", background: { color: C.background2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.4, w: CW, h: 1.25, fontSize: 34, bold: true, color: C.text1, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: W - M - 0.8, y: 6.98, w: 0.8, h: 0.3, fontSize: 12, color: C.accent3, align: "right" },
});
pres.defineSlideMaster({
  title: "DARK", background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.6, w: CW, h: 1.1, fontSize: 40, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: W - M - 0.8, y: 6.98, w: 0.8, h: 0.3, fontSize: 12, color: C.accent4, align: "right" },
});

// ---------- helpers (fresh option objects every call) ----------
const shadow = () => ({ type: "outer", color: "0F2A33", opacity: 0.12, blur: 8, offset: 2, angle: 90 });
function card(s, name, x, y, w, h, fill) {
  s.addShape(pres.ShapeType.roundRect, { objectName: name, x, y, w, h, rectRadius: 0.12, fill: { color: fill || C.background1 }, line: { color: C.accent5, width: 0.75 }, shadow: shadow() });
}
function badge(s, name, n, x, y, d, fill) {
  s.addShape(pres.ShapeType.ellipse, { objectName: name, x, y, w: d, h: d, fill: { color: fill || C.accent1 }, line: { type: "none" } });
  s.addText(String(n), { objectName: name + " number", isTextBox: true, x, y, w: d, h: d, align: "center", valign: "middle", fontSize: 16, bold: true, color: C.background1, margin: 0 });
}
function foot(s, text) {
  s.addText(text, { objectName: "Source note", isTextBox: true, x: M, y: 6.98, w: CW - 1.2, h: 0.3, fontSize: 12, color: C.accent3, margin: 0, valign: "middle" });
}
function title(s, t) { s.addText(t, { placeholder: "title" }); }
function ripples(s, cx, cy, color) {
  [0.6, 1.2, 1.9, 2.7].forEach((r, i) => s.addShape(pres.ShapeType.ellipse, {
    objectName: "Ripple " + (i + 1), x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, fill: { type: "none" }, line: { color, width: 1.5 - i * 0.25, transparency: 20 + i * 15 } }));
}
function cardText(s, x, y, w, head, lines, hs, bs) {
  s.addText(head, { objectName: head + " heading", isTextBox: true, x, y, w, h: 0.45, fontSize: hs || 20, bold: true, color: C.accent1, margin: 0, valign: "top" });
  s.addText(lines.map((t, i) => ({ text: t, options: { bullet: lines.length > 1, breakLine: i < lines.length - 1, paraSpaceAfter: 6 } })),
    { objectName: head + " body", isTextBox: true, x, y: y + 0.5, w, h: 2.7, fontSize: bs || 16, color: C.text2, margin: 0, valign: "top", fit: "none" });
}

// ============ SECTION 1 ============
pres.addSection({ title: "Problem and context" });

// --- 0 Title
{
  const s = pres.addSlide({ masterName: "TITLE", sectionTitle: "Problem and context" });
  ripples(s, 11.0, 3.6, C.accent4);
  s.addText("INTERMITTENT WATER SUPPLY", { objectName: "Eyebrow", isTextBox: true, x: M, y: 1.7, w: 8, h: 0.4, fontSize: 16, bold: true, charSpacing: 4, color: C.accent4, margin: 0 });
  s.addText("Can reinforcement learning share scarce water fairly?", { objectName: "Title", isTextBox: true, x: M, y: 2.2, w: 8.2, h: 2.2, fontSize: 48, bold: true, color: C.background1, margin: 0, valign: "top" });
  s.addText("Equity-aware zone scheduling, tested in simulation against a tuned fixed daily schedule", { objectName: "Subtitle", isTextBox: true, x: M, y: 4.55, w: 8.2, h: 1.0, fontSize: 22, color: C.accent5, margin: 0, valign: "top" });
  s.addText("[Team names]  ·  [Course]  ·  2 November 2026", { objectName: "Byline", isTextBox: true, x: M, y: 6.7, w: 9, h: 0.4, fontSize: 16, color: C.accent4, margin: 0 });
  s.addNotes("Open with the question. Many cities supply water only a few hours a day. We asked whether a learned policy can decide which areas get water, so that more water is served and the worst-off area is protected. Short answer, which we will earn at the end: sometimes, not always, and we can say when. Fill in the team, course and date placeholders before presenting.");
}

// --- 1 Problem
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem and context" });
  title(s, "Water arrives for a few hours, so who gets it first matters");
  const cards = [
    ["Supply is rationed", "Zones receive water only some hours per day."],
    ["Households store water", "Roof tanks fill when water arrives. The utility cannot see their levels."],
    ["Tanks can widen inequity", "Households with better hydraulic access fill first (Hendrickson & Sela, 2024)."],
  ];
  const cw = (CW - 0.5) / 3;
  cards.forEach(([h, b], i) => {
    const x = M + i * (cw + 0.25);
    card(s, "Card " + (i + 1), x, 1.95, cw, 2.85);
    badge(s, "Badge " + (i + 1), i + 1, x + 0.3, 2.2, 0.55);
    s.addText(h, { objectName: "Card heading " + (i + 1), isTextBox: true, x: x + 0.3, y: 2.95, w: cw - 0.6, h: 0.45, fontSize: 20, bold: true, color: C.text1, margin: 0 });
    s.addText(b, { objectName: "Card body " + (i + 1), isTextBox: true, x: x + 0.3, y: 3.5, w: cw - 0.6, h: 1.2, fontSize: 16, color: C.text2, margin: 0, valign: "top" });
  });
  s.addText("Can a learned policy serve more water and protect the worst-off zone?", { objectName: "Research question", isTextBox: true, x: M, y: 5.3, w: CW, h: 1.0, fontSize: 28, bold: true, italic: true, color: C.accent1, margin: 0, valign: "middle" });
  foot(s, "Source: Hendrickson & Sela (2024), abstract");
  s.addNotes("Explain intermittent supply. The decision is: each hour, which zones are open. Stress the hidden household tanks: the utility sees pressure and flow, not what is in the tanks. Do not add a city example unless you have read a source for it.");
}

// --- 2 Related work
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem and context" });
  title(s, "We found no RL for equity in intermittent supply");
  const cols = [
    ["Optimisation work", ["Hendrickson & Sela (2024): Bayesian-optimised valve schedules with household tanks", "Kurian et al. (2023): mixed-integer schedules for rural networks", "A 2026 npj Clean Water paper on equitable supply is reported; not yet read"]],
    ["RL in water networks", ["Pump scheduling: Pei 2025, Hajgató 2020", "Pressure control: Belfadil 2024", "Valves for contamination: Hu 2020", "Objectives are cost or pressure, not equity"]],
    ["Fair RL theory", ["Siddique et al. (2020): generalized Gini welfare over per-user returns", "Our equity bonus is simpler: a daily bonus on the worst zone"]],
  ];
  const cw = (CW - 0.5) / 3;
  cols.forEach(([h, ls], i) => {
    const x = M + i * (cw + 0.25);
    card(s, "Column card " + (i + 1), x, 1.95, cw, 3.55);
    cardText(s, x + 0.3, 2.15, cw - 0.6, h, ls, 18, 15);
  });
  s.addText("In our search we found no RL paper combining intermittent supply, zone scheduling, equity and household storage. The search was not exhaustive.", { objectName: "Gap statement", isTextBox: true, x: M, y: 5.75, w: CW, h: 0.9, fontSize: 18, italic: true, color: C.text2, margin: 0, valign: "middle" });
  foot(s, "Source: docs/related_work.md (mostly abstract-level checks)");
  s.addNotes("Position the work. The closest prior work is optimisation, so our fair baseline is an optimised fixed schedule. Say 'in our search', never 'first'. Do NOT claim novelty over the 2026 npj Clean Water paper until someone has read it.");
}

// ============ SECTION 2 ============
pres.addSection({ title: "Environment and methods" });

// --- 3 Environment
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Environment and methods" });
  title(s, "A 4-zone network with hourly open/close decisions");
  const items = [
    ["Network", "EPANET Net3: 59 demand nodes in 4 zones."],
    ["Decision", "Each hour, choose which zones are open (16 combinations)."],
    ["Hidden state", "Household roof tanks (0.3 to 0.8 days of use), not observed."],
    ["Budget", "Daily source volume of 50 to 90% of demand, known one day ahead."],
    ["Reward", "Minus unmet demand each hour, plus an end-of-day bonus for the worst zone (weight λ)."],
    ["Episode", "3 days = 72 decisions; EPANET pressure-dependent hydraulics."],
  ];
  const cw = (CW - 0.5) / 3, ch = 2.2;
  items.forEach(([h, b], i) => {
    const x = M + (i % 3) * (cw + 0.25), y = 1.95 + Math.floor(i / 3) * (ch + 0.25);
    card(s, "Env card " + (i + 1), x, y, cw, ch);
    s.addText(h, { objectName: "Env heading " + (i + 1), isTextBox: true, x: x + 0.3, y: y + 0.2, w: cw - 0.6, h: 0.45, fontSize: 20, bold: true, color: C.accent1, margin: 0 });
    s.addText(b, { objectName: "Env body " + (i + 1), isTextBox: true, x: x + 0.3, y: y + 0.75, w: cw - 0.6, h: 1.3, fontSize: 16, color: C.text2, margin: 0, valign: "top" });
  });
  foot(s, "Simulation only. Tank sizes, surge factor and budgets are assumptions (docs/assumptions.md)");
  s.addNotes("Walk through one hour: pick zones; households request water to refill tanks (up to alpha times normal demand); EPANET computes what actually arrives given pressure; tanks fill, households draw; reward. Mention partial observability: hidden tanks make this a POMDP. State clearly that tank sizes and the surge factor are assumptions.");
}

// --- 4 v1 vs v2
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Environment and methods" });
  title(s, "v1 was too easy, so v2 makes the hydraulics bind");
  const cw = (CW - 0.3) / 2;
  const data = [
    ["v1: saturated", "99%", "of the budget ceiling reached by PPO (0.767 of 0.773)", "Pressure thresholds of 10, 20 and 30 m gave identical results."],
    ["v2: demand ×8", "0.56 to 0.72", "mean supply across methods", "Opening every zone at once now starves the network, and pressure thresholds matter."],
  ];
  data.forEach(([h, big, cap, note], i) => {
    const x = M + i * (cw + 0.3);
    card(s, "Version card " + (i + 1), x, 1.95, cw, 4.5);
    s.addText(h, { objectName: "Version heading " + (i + 1), isTextBox: true, x: x + 0.4, y: 2.15, w: cw - 0.8, h: 0.5, fontSize: 22, bold: true, color: C.accent1, margin: 0 });
    s.addText(big, { objectName: "Big stat " + (i + 1), isTextBox: true, x: x + 0.4, y: 2.8, w: cw - 0.8, h: 1.1, fontSize: 60, bold: true, color: C.text1, margin: 0, valign: "middle" });
    s.addText(cap, { objectName: "Stat caption " + (i + 1), isTextBox: true, x: x + 0.4, y: 3.95, w: cw - 0.8, h: 0.8, fontSize: 18, color: C.text2, margin: 0, valign: "top" });
    s.addText(note, { objectName: "Version note " + (i + 1), isTextBox: true, x: x + 0.4, y: 5.0, w: cw - 0.8, h: 1.2, fontSize: 16, italic: true, color: C.accent3, margin: 0, valign: "top" });
  });
  foot(s, "Source: docs/PROJECT_LOG.md, results_v2/. All following results are v2.");
  s.addNotes("A methodological point worth making: a result near the budget ceiling cannot show a method is good. We diagnosed that the first benchmark was saturated and changed it before drawing conclusions. Everything that follows is v2.");
}

// --- 5 Methods
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Environment and methods" });
  title(s, "One test set, many methods");
  const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.accent1 }, fontSize: 16 } });
  const row = (a, b, c, hi) => [a, b, c].map((t, j) => ({ text: t, options: { bold: hi || j === 0, color: hi ? C.accent2 : C.text2, fill: { color: hi ? "F6E3D3" : C.background1 }, fontSize: 15 } }));
  const rows = [
    [hdr("Group"), hdr("Methods"), hdr("Runs")],
    row("Simple rules", "random, all-open, rota, greedy k1 and k2", "1 each"),
    row("Privileged rule", "greedy on hidden tank levels (not deployable)", "1"),
    row("Tuned fixed schedule", "cross-entropy search, 40 iterations, population 60", "3", true),
    row("Reinforcement learning", "PPO, PPO + domain randomisation, DQN, PPO without equity term", "5 seeds each"),
    row("Recurrent RL", "LSTM PPO, LSTM PPO + randomisation", "3 seeds each"),
    row("Equity-weight sweep", "PPO with λ = 0, 0.5, 1, 2, 4", "2 to 5 seeds"),
    row("Oracle", "hindsight upper bound (uses the future)", "30 scenarios"),
  ];
  s.addTable(rows, { objectName: "Methods table", x: M, y: 1.85, w: CW, colW: [2.9, 6.6, 2.6], border: { type: "solid", pt: 0.5, color: "CBD5D2" }, margin: [0.07, 0.12, 0.07, 0.12], valign: "middle" });
  s.addText("Test scenarios use seeds 10000 and up, never used in training: 100 scenarios for the default condition, 50 for each other condition.", { objectName: "Protocol note", isTextBox: true, x: M, y: 6.2, w: CW, h: 0.6, fontSize: 16, italic: true, color: C.text2, margin: 0, valign: "middle" });
  foot(s, "Orange = the tuned fixed schedule, the baseline to beat");
  s.addNotes("The tuned fixed schedule is the strong baseline an expert would build: a 24-hour timetable repeated every day, optimised on training scenarios. The oracle is only a reference: it sees the future.");
}

// ============ SECTION 3 ============
pres.addSection({ title: "Results" });

// --- 6 Main result
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
  title(s, "On matching conditions, the tuned schedule is hard to beat");
  const hdr = (t, al) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.accent1 }, fontSize: 15, align: al || "left" } });
  const row = (n, a, b, hi) => [n, a, b].map((t, j) => ({ text: t, options: { bold: hi || j === 0, color: hi ? C.accent2 : C.text2, fill: { color: hi ? "F6E3D3" : C.background1 }, fontSize: 14, align: j ? "center" : "left" } }));
  const rows = [
    [hdr("Method"), hdr("Mean supply [95% CI]", "center"), hdr("Worst zone [95% CI]", "center")],
    row("Tuned fixed schedule (3)", "0.716 [0.706, 0.725]", "0.630 [0.623, 0.638]", true),
    row("PPO (5)", "0.716 [0.707, 0.725]", "0.601 [0.592, 0.609]"),
    row("PPO + domain randomisation (5)", "0.711 [0.703, 0.720]", "0.612 [0.604, 0.621]"),
    row("DQN (5)", "0.714 [0.705, 0.723]", "0.590 [0.582, 0.597]"),
    row("PPO, no equity term (5)", "0.718 [0.709, 0.727]", "0.564 [0.553, 0.574]"),
    row("Random", "0.672 [0.664, 0.680]", "0.527 [0.518, 0.537]"),
  ];
  s.addTable(rows, { objectName: "Main results table", x: M, y: 1.9, w: 8.1, colW: [3.3, 2.4, 2.4], border: { type: "solid", pt: 0.5, color: "CBD5D2" }, margin: [0.09, 0.1, 0.09, 0.1], valign: "middle" });
  const stats = [["Mean supply", "tie", "PPO minus tuned: 0.000 [-0.001, 0.001]"], ["Worst zone", "-0.030", "PPO is lower; CI [-0.031, -0.028]"], ["Return", "-0.52", "PPO is lower; CI [-0.59, -0.46]"]];
  stats.forEach(([lbl, big, sub], i) => {
    const y = 1.9 + i * 1.5;
    card(s, "Stat card " + (i + 1), 9.0, y, 3.73, 1.35);
    s.addText(lbl, { objectName: "Stat label " + (i + 1), isTextBox: true, x: 9.2, y: y + 0.1, w: 3.3, h: 0.3, fontSize: 14, bold: true, color: C.accent3, margin: 0 });
    s.addText(big, { objectName: "Stat value " + (i + 1), isTextBox: true, x: 9.2, y: y + 0.38, w: 3.3, h: 0.5, fontSize: 30, bold: true, color: C.text1, margin: 0, valign: "middle" });
    s.addText(sub, { objectName: "Stat sub " + (i + 1), isTextBox: true, x: 9.2, y: y + 0.9, w: 3.35, h: 0.35, fontSize: 12, color: C.accent3, margin: 0, valign: "top" });
  });
  s.addText("Paired differences versus the tuned schedule, 100 test scenarios", { objectName: "Stat caption", isTextBox: true, x: 9.0, y: 6.4, w: 3.73, h: 0.45, fontSize: 12, color: C.accent3, margin: 0, valign: "top" });
  foot(s, "Source: results_v2/summary.csv, paired_vs_ce_tuned.csv. Numbers in brackets = training runs.");
  s.addNotes("Read the table in two sentences: RL matches the tuned timetable on how much water is delivered, but not on protecting the worst zone. Removing the equity term makes the worst zone clearly worse (0.564), so the equity term does something. Robustness check: every PPO run is below every tuned-schedule run on worst zone and return in the default condition. Seed variance is not in the confidence intervals.");
}

// --- 7 Oracle
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
  title(s, "Little headroom is left above the tuned schedule");
  const big = [["Oracle", "-8.49", C.text1, "future-aware bound"], ["Tuned fixed schedule", "-9.15", C.accent2, "deployable"], ["PPO", "-9.67", C.accent1, "deployable"]];
  const cw = (CW - 0.5) / 3;
  big.forEach(([lbl, val, col, sub], i) => {
    const x = M + i * (cw + 0.25);
    card(s, "Return card " + (i + 1), x, 1.95, cw, 2.7);
    s.addText(lbl, { objectName: "Return label " + (i + 1), isTextBox: true, x: x + 0.3, y: 2.1, w: cw - 0.6, h: 0.45, fontSize: 20, bold: true, color: C.text2, margin: 0 });
    s.addText(val, { objectName: "Return value " + (i + 1), isTextBox: true, x: x + 0.3, y: 2.6, w: cw - 0.6, h: 1.2, fontSize: 66, bold: true, color: col, margin: 0, valign: "middle" });
    s.addText("return, higher is better; " + sub, { objectName: "Return caption " + (i + 1), isTextBox: true, x: x + 0.3, y: 3.9, w: cw - 0.6, h: 0.6, fontSize: 14, color: C.accent3, margin: 0, valign: "top" });
  });
  s.addText([
    { text: "Mean supply: oracle 0.725 · tuned schedule 0.716.  Worst zone: oracle 0.631 · tuned schedule 0.630.", options: { breakLine: true } },
    { text: "Caveat: the oracle uses 30 scenarios and sees future budgets and hidden tanks. The other methods use 100 scenarios, so no exact \"percent of gap closed\" is claimed." },
  ], { objectName: "Oracle notes", isTextBox: true, x: M, y: 4.95, w: CW, h: 1.6, fontSize: 18, color: C.text2, margin: 0, valign: "top", paraSpaceAfter: 10 });
  foot(s, "Source: results_v2/oracle.csv, README.md (M1 results table)");
  s.addNotes("The oracle is an upper bound that knows future budgets and the hidden tanks. The tuned schedule is already close to it on supply; some gap remains on the training objective (return). Do not state a percentage of gap closed because the sample sizes differ.");
}

// --- 8 Equity
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
  title(s, "A larger equity weight lifts the worst zone at a small cost");
  const h = 4.75, w = h * 1.244;
  s.addImage({ path: IMG("pareto_lambda.png"), x: M, y: 1.9, w, h, altText: "Mean supply versus worst-zone supply for PPO at lambda 0, 0.5, 1, 2 and 4, with the tuned schedule, DQN and PPO with randomisation" });
  const x = M + w + 0.5, tw = W - M - x;
  s.addText([
    { text: "Worst zone: 0.573 → 0.635 as λ goes from 0 to 4", options: { bullet: true, breakLine: true } },
    { text: "Mean supply: 0.718 → 0.708", options: { bullet: true, breakLine: true } },
    { text: "λ = 4 reaches the tuned schedule's worst zone (0.635 vs 0.630) for about 0.008 less mean supply", options: { bullet: true } },
  ], { objectName: "Equity findings", isTextBox: true, x, y: 1.95, w: tw, h: 2.6, fontSize: 18, color: C.text2, margin: 0, valign: "top", paraSpaceAfter: 10 });
  card(s, "Honesty card", x, 4.75, tw, 1.9, C.background1);
  s.addText("Handle with care: 2 to 5 seeds per point, not monotone (λ = 2 sits below λ = 1), intervals overlap. λ is a reward penalty, not a constraint.", { objectName: "Honesty text", isTextBox: true, x: x + 0.25, y: 4.9, w: tw - 0.5, h: 1.6, fontSize: 15, italic: true, color: C.text2, margin: 0, valign: "middle" });
  foot(s, "Source: results_v2/summary.csv (default condition); figure: plots/out/pareto_lambda.png");
  s.addNotes("λ is the knob that trades efficiency for fairness. Do not call it Lagrangian or constrained RL. Our bonus is a max-min-style term and is NOT the generalized-Gini optimisation of Siddique et al.; say so if asked.");
}

// --- 8b Learning curves
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
  title(s, "PPO matches the schedule on mean supply by 100k steps, but the worst zone is still rising");
  const w = 7.7, h = w / 2.381;
  s.addImage({ path: IMG("learning_curves.png"), x: M, y: 2.0, w, h, altText: "Learning curves for three PPO seeds: mean supply and worst-zone supply versus training steps, with the tuned schedule as a dashed line" });
  const x = M + w + 0.4, tw = W - M - x;
  s.addText([
    { text: "Mean supply flattens near 0.70 to 0.72 after about 100k steps, at the tuned schedule's level (0.716).", options: { bullet: true, breakLine: true } },
    { text: "Worst zone ends at 0.60 to 0.62 after 300k steps, still below the schedule's 0.630 and still creeping up.", options: { bullet: true, breakLine: true } },
    { text: "We do not claim convergence on the worst zone.", options: { bullet: true } },
  ], { objectName: "Curve findings", isTextBox: true, x, y: 2.0, w: tw, h: 3.0, fontSize: 17, color: C.text2, margin: 0, valign: "top", paraSpaceAfter: 10 });
  card(s, "Curve caveat card", x, 5.1, tw, 1.55, C.background1);
  s.addText("3 seeds, one training length (300k steps). Each point is 10 test scenarios, so single points are noisy.", { objectName: "Curve caveat", isTextBox: true, x: x + 0.2, y: 5.2, w: tw - 0.4, h: 1.35, fontSize: 14, italic: true, color: C.text2, margin: 0, valign: "middle" });
  foot(s, "Source: plots/train_curves.py runs, seeds 0 to 2, test seeds 10000 to 10009; figure plots/out/learning_curves.png");
  s.addNotes("Sample-efficiency evidence. Mean supply is level with the tuned schedule from about 100k steps; the worst zone is slower and is still rising at 300k, so more training or a larger lambda might close the gap, but we did not test that. Curves use 10 test scenarios per point and 3 seeds, so they are indicative only. The final-point values differ slightly from the 100-scenario table (PPO worst zone 0.601).");
}

// --- 9 Shift
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
  title(s, "RL helps only when conditions move away from the tuning");
  const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.accent1 }, fontSize: 15, align: "center" } });
  const cell = (t) => {
    const k = t.startsWith("better") ? 0 : t.startsWith("worse") ? 1 : 2;
    return { text: t, options: { bold: k === 0, italic: k === 2, color: k === 0 ? C.accent1 : k === 1 ? C.text2 : C.accent3, fontSize: 14, align: "center", fill: { color: C.background1 } } };
  };
  const lead = (t) => ({ text: t, options: { bold: true, color: C.text2, fontSize: 14, fill: { color: C.background1 } } });
  const rows = [
    [{ text: "Condition", options: { bold: true, color: C.background1, fill: { color: C.accent1 }, fontSize: 15 } }, hdr("PPO"), hdr("PPO + DR"), hdr("DQN")],
    [lead("default"), cell("worse (-0.52)"), cell("worse (-0.77)"), cell("worse (-0.86)")],
    [lead("alpha = 2"), cell("better (+1.14)"), cell("better (+1.66)"), cell("better (+2.01)")],
    [lead("alpha = 8"), cell("worse (-0.20)"), cell("tie (+0.08)"), cell("worse (-0.81)")],
    [lead("small tanks"), cell("tie (-0.15)"), cell("tie (+0.05)"), cell("better (+1.14)")],
    [lead("other 6 conditions*"), cell("worse"), cell("worse"), cell("worse")],
  ];
  s.addTable(rows, { objectName: "Shift table", x: M, y: 1.9, w: 8.2, colW: [2.9, 1.8, 1.8, 1.7], border: { type: "solid", pt: 0.5, color: "CBD5D2" }, margin: [0.1, 0.1, 0.1, 0.1], valign: "middle" });
  s.addText("Return versus the tuned schedule, with the paired 95% interval deciding better, worse or tie.  *abundant, five days, large tanks, noisy demand, 10 m and 30 m pressure.", { objectName: "Table note", isTextBox: true, x: M, y: 5.65, w: 8.2, h: 0.9, fontSize: 13, italic: true, color: C.accent3, margin: 0, valign: "top" });
  card(s, "Why card", 9.1, 1.9, 3.63, 4.65);
  s.addText([
    { text: "Why alpha = 2 differs", options: { bold: true, color: C.accent1, fontSize: 18, breakLine: true } },
    { text: "A fixed timetable cannot adapt when the surge cap changes; a reactive policy can. Alpha = 2 is outside the randomisation range (3 to 6).", options: { fontSize: 15, breakLine: true } },
    { text: "The schedule was tuned on the default condition only.", options: { fontSize: 15, breakLine: true } },
    { text: "LSTM PPO is below PPO, and LSTM with randomisation reaches only 0.469 on the worst zone: a negative result.", options: { fontSize: 15 } },
  ], { objectName: "Why text", isTextBox: true, x: 9.35, y: 2.05, w: 3.15, h: 4.4, color: C.text2, margin: 0, valign: "top", paraSpaceAfter: 8 });
  foot(s, "Source: results_v2/paired_vs_ce_tuned.csv. Overall PPO is worse in 8 of 10 non-scarce conditions, better in 1, tied in 1.");
  s.addNotes("A fixed timetable cannot adapt when the surge cap changes; a reactive policy can. That is the one place RL wins clearly. Overall PPO is worse in 8 of 10 non-scarce conditions, better in 1, tied in 1. The scarce condition is excluded because every method scores about the same for mean supply there.");
}

// --- 10 Heatmap
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
  title(s, "Almost every RL method trails on the worst zone");
  const h = 5.3, w = h * 1.249;
  s.addImage({ path: IMG("heatmap_worst_vs_baseline.png"), x: M, y: 1.55, w, h, altText: "Heatmap of worst-zone supply difference versus the tuned schedule for each method and condition; blue means better than the schedule" });
  const x = M + w + 0.4, tw = W - M - x;
  s.addText([
    { text: "Blue = better than the tuned schedule, red = worse (paired means).", options: { bullet: true, breakLine: true } },
    { text: "PPO with λ = 4 is the only RL row near or above zero in most conditions.", options: { bullet: true, breakLine: true } },
    { text: "The alpha = 2 column is where RL clearly wins.", options: { bullet: true } },
  ], { objectName: "Heatmap reading", isTextBox: true, x, y: 1.7, w: tw, h: 4.5, fontSize: 18, color: C.text2, margin: 0, valign: "top", paraSpaceAfter: 12 });
  foot(s, "Source: results_v2/episodes.csv via plots/make_plots.py (scarce excluded)");
  s.addNotes("Point at the red block, then at the alpha2 column. This is the regime map: where RL helps and where it does not.");
}

// ============ SECTION 4 ============
pres.addSection({ title: "Conclusions" });

// --- 11 Limits
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Conclusions" });
  title(s, "What this study cannot claim");
  const items = [
    "One simulated network, no field data.",
    "Tank sizes, surge factor and budgets are assumed; 0.3 to 0.8 days is probably below real storage.",
    "2 to 5 training seeds per method; the oracle uses 30 scenarios.",
    "The fixed schedule was tuned on one condition only.",
    "The equity weight is a reward penalty, not a constraint.",
    "Literature checked mostly at abstract level; forward-citation search not done.",
  ];
  const cw = (CW - 0.5) / 3, ch = 2.15;
  items.forEach((t, i) => {
    const x = M + (i % 3) * (cw + 0.25), y = 1.95 + Math.floor(i / 3) * (ch + 0.25);
    card(s, "Limit card " + (i + 1), x, y, cw, ch);
    badge(s, "Limit badge " + (i + 1), i + 1, x + 0.3, y + 0.25, 0.5, C.accent3);
    s.addText(t, { objectName: "Limit text " + (i + 1), isTextBox: true, x: x + 0.3, y: y + 0.9, w: cw - 0.6, h: 1.1, fontSize: 16, color: C.text2, margin: 0, valign: "top" });
  });
  foot(s, "Source: docs/assumptions.md, docs/STUDY_GUIDE.md section 10");
  s.addNotes("Examiners respect this slide. For each limit, say what it would change: one network limits generality; assumed tank sizes limit realism; few seeds mean the intervals understate uncertainty; a schedule tuned on one condition may look worse or better under other tuning.");
}

// --- 12 Conclusion
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Conclusions" });
  ripples(s, 12.9, 0.5, C.accent1);
  title(s, "What we can say");
  s.addText([
    { text: "A tuned fixed daily schedule matches PPO on mean supply and beats it on worst-zone supply under matching conditions.", options: { bullet: true, breakLine: true } },
    { text: "RL wins when the surge cap changes (alpha = 2) and, for DQN, with small tanks.", options: { bullet: true, breakLine: true } },
    { text: "A larger equity weight raises worst-zone supply for a small loss in mean supply.", options: { bullet: true } },
  ], { objectName: "Conclusions", isTextBox: true, x: M, y: 1.9, w: 10.4, h: 2.9, fontSize: 24, color: C.background1, margin: 0, valign: "top", paraSpaceAfter: 14 });
  s.addText([
    { text: "Not claimed: ", options: { bold: true, color: C.accent4 } },
    { text: "\"first\"; \"RL beats optimised scheduling\" without \"under the shifts we tested\"; \"constrained RL\".", options: { color: C.accent5, breakLine: true } },
    { text: "Next: ", options: { bold: true, color: C.accent4 } },
    { text: "a second network, measured tank sizes, fairness as a constraint, a preference-conditioned policy.", options: { color: C.accent5 } },
  ], { objectName: "Claims and next steps", isTextBox: true, x: M, y: 5.0, w: 10.4, h: 1.7, fontSize: 18, margin: 0, valign: "top", paraSpaceAfter: 8 });
  s.addNotes("Repeat the three points, then the one-line takeaway: use a good timetable by default, and use RL where conditions change.");
}

// ============ BACKUP ============
pres.addSection({ title: "Backup" });
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Backup" });
  title(s, "Backup: efficiency versus equity for all methods");
  const h = 4.7, w = h * 1.505;
  s.addImage({ path: IMG("scatter_mean_vs_worst.png"), x: M, y: 1.9, w, h, altText: "Scatter of mean supply against worst-zone supply for all methods with 95% intervals, and the oracle" });
  s.addText("Each point is a method family on the default condition (95% CI over scenarios). The star is the oracle (30 scenarios, uses the future).", { objectName: "Backup caption", isTextBox: true, x: M + w + 0.4, y: 2.0, w: W - M - (M + w + 0.4), h: 3.0, fontSize: 16, color: C.text2, margin: 0, valign: "top" });
  foot(s, "Source: plots/out/scatter_mean_vs_worst.png");
  s.addNotes("Backup only. Use if asked for the full efficiency-versus-equity picture.");
}
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Backup" });
  title(s, "Backup: mean supply differs by only about ±0.01 for PPO");
  const h = 4.8, w = h * 1.249;
  s.addImage({ path: IMG("heatmap_mean_vs_baseline.png"), x: M, y: 1.85, w, h, altText: "Heatmap of mean supply difference versus the tuned schedule for each method and condition" });
  s.addText("PPO's mean supply is within about 0.01 of the tuned schedule in every non-scarce condition; the differences that matter are on the worst zone and on return.", { objectName: "Backup caption 2", isTextBox: true, x: M + w + 0.4, y: 2.0, w: W - M - (M + w + 0.4), h: 3.0, fontSize: 16, color: C.text2, margin: 0, valign: "top" });
  foot(s, "Source: plots/out/heatmap_mean_vs_baseline.png (paired means; scarce excluded)");
  s.addNotes("Backup only.");
}
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Backup" });
  title(s, "Backup: reward and tank balance");
  const eq = [
    ["Hourly reward", "− Σ unmet demand ÷ (average hourly consumption)"],
    ["End-of-day bonus", "+ λ · (worst zone's supply ratio that day) · 24 / Z   (Z = 4 zones, λ = 1 by default)"],
    ["Household tank", "L ← L + delivered volume − overflow;  served = min(L, want);  unmet = want − served"],
    ["Request", "request = min(α · mean demand, refill need + use);  EPANET returns the delivery"],
  ];
  eq.forEach(([h, t], i) => {
    const y = 1.95 + i * 1.15;
    card(s, "Equation card " + (i + 1), M, y, CW, 1.0);
    s.addText(h, { objectName: "Equation label " + (i + 1), isTextBox: true, x: M + 0.3, y: y + 0.12, w: 2.7, h: 0.76, fontSize: 18, bold: true, color: C.accent1, margin: 0, valign: "middle" });
    s.addText(t, { objectName: "Equation text " + (i + 1), isTextBox: true, x: M + 3.1, y: y + 0.12, w: CW - 3.4, h: 0.76, fontSize: 16, color: C.text2, margin: 0, valign: "middle" });
  });
  foot(s, "Source: iws_env.py, docs/STUDY_GUIDE.md section 4");
  s.addNotes("Backup only. Equations as implemented in iws_env.py.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
