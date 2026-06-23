// FORGE AI — 10-slide Introduction Deck
// Generated with PptxGenJS
const pptxgen = require("pptxgenjs");
const fs = require("fs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "FORGE AI";
pres.title = "FORGE AI — Introduction Deck";

// ============================================================
// Color System
// ============================================================
const C = {
  dark:    "0F172A",
  dark2:   "1E293B",
  teal:    "0D9488",
  tealL:   "14B8A6",
  tealBg:  "CCFBF1",
  light:   "F1F5F9",
  white:   "FFFFFF",
  cream:   "F8FAFC",
  muted:   "64748B",
  body:    "334155",
  amber:   "F59E0B",
  emerald:"10B981",
  red:     "EF4444",
  slate3:  "CBD5E1",
  slate2:  "E2E8F0",
};

const TOTAL = 10;
const FW = 10;   // slide width
const FH = 5.625; // slide height

// ============================================================
// Helpers
// ============================================================

function addTopBar(slide) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: FW, h: 0.03, fill: { color: C.teal },
  });
}

function addFooter(slide, text) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.3, w: 10, h: 0.325, fill: { color: C.cream },
  });
  slide.addText(text, {
    x: 0.6, y: 5.3, w: 8, h: 0.325,
    fontSize: 7.5, color: C.muted, fontFace: "Calibri", margin: 0, valign: "middle", italic: true,
  });
}

function pageNum(slide, n) {
  slide.addText(`${n} / ${TOTAL}`, {
    x: 8.5, y: 5.18, w: 1, h: 0.3,
    fontSize: 8, color: C.muted, align: "right", fontFace: "Calibri", margin: 0,
  });
}

function darkPageNum(slide, n) {
  slide.addText(`${n} / ${TOTAL}`, {
    x: 8.5, y: 5.18, w: 1, h: 0.3,
    fontSize: 8, color: "475569", align: "right", fontFace: "Calibri", margin: 0,
  });
}

function slideTitle(slide, title, subtitle) {
  slide.addText(title, {
    x: 0.7, y: 0.3, w: 8.6, h: 0.55,
    fontSize: 30, fontFace: "Arial Black", color: C.dark, margin: 0, bold: true,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.7, y: 0.85, w: 8.6, h: 0.35,
      fontSize: 13, fontFace: "Calibri", color: C.muted, margin: 0,
    });
  }
}

function card(slide, x, y, w, h, color) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: color || C.white },
    shadow: { type: "outer", blur: 3, offset: 1, angle: 135, color: "000000", opacity: 0.07 },
  });
}

const mkShadow = () => ({ type: "outer", blur: 3, offset: 1, angle: 135, color: "000000", opacity: 0.07 });

// ============================================================
// SLIDE 1 — TITLE
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.dark };

  // Decorative geometric shapes
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.8, y: -1.2, w: 5, h: 4.5, fill: { color: C.teal, transparency: 88 }, rotate: 25,
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.8, y: 2.2, w: 5.5, h: 4.5, fill: { color: C.tealL, transparency: 92 }, rotate: -18,
  });

  // Logo mark
  s.addText("⚒️", {
    x: 0.8, y: 0.6, w: 0.8, h: 0.8,
    fontSize: 36, margin: 0,
  });

  // Main title
  s.addText("FORGE AI", {
    x: 0.8, y: 1.4, w: 7, h: 1.1,
    fontSize: 52, fontFace: "Arial Black", color: C.white, margin: 0, bold: true, charSpacing: 2,
  });

  // Tagline
  s.addText("Revolutionize Your Innovation Process", {
    x: 0.8, y: 2.5, w: 7, h: 0.55,
    fontSize: 22, fontFace: "Calibri", color: C.tealL, margin: 0,
  });

  // Subtitle
  s.addText("The AI-Native R&D Platform", {
    x: 0.8, y: 3.05, w: 7, h: 0.45,
    fontSize: 15, fontFace: "Calibri", color: C.muted, margin: 0,
  });

  // Bottom tag
  s.addText("Built by a Chemist  ·  Human in the Loop  ·  For Every Materials Company", {
    x: 0.8, y: 4.7, w: 8, h: 0.35,
    fontSize: 10, fontFace: "Calibri", color: C.muted, margin: 0, italic: true,
  });

  darkPageNum(s, 1);
})();

// ============================================================
// SLIDE 2 — THE R&D BOTTLENECK
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.cream };
  addTopBar(s);

  slideTitle(s, "The R&D Bottleneck", "Why materials innovation takes too long");

  // Problem stat callout — big number
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 1.5, w: 3.8, h: 1.3,
    fill: { color: C.teal },
    shadow: mkShadow(),
  });
  s.addText("80%", {
    x: 0.7, y: 1.5, w: 3.8, h: 0.75,
    fontSize: 48, fontFace: "Arial Black", color: C.white, align: "center", margin: 0, bold: true,
  });
  s.addText("of R&D time spent on\nsearching & reading — not science", {
    x: 0.7, y: 2.2, w: 3.8, h: 0.55,
    fontSize: 11, fontFace: "Calibri", color: C.white, align: "center", margin: 0,
  });

  // Pain points — left column
  const pains = [
    { icon: "🔍", text: "Screen 50+ patents per formulation" },
    { icon: "📋", text: "Manual extraction into spreadsheets" },
    { icon: "🧪", text: "DOE based on intuition, not evidence" },
    { icon: "📄", text: "Days spent writing reports & slides" },
  ];
  pains.forEach((p, i) => {
    const y = 1.5 + i * 0.72;
    card(s, 5.0, y, 4.3, 0.6, C.white);
    s.addText(p.icon, {
      x: 5.2, y, w: 0.45, h: 0.6,
      fontSize: 16, align: "center", valign: "middle", margin: 0,
    });
    s.addText(p.text, {
      x: 5.7, y, w: 3.4, h: 0.6,
      fontSize: 12.5, fontFace: "Calibri", color: C.body, valign: "middle", margin: 0,
    });
  });

  // Bottom: "8 days vs 5 minutes"
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 4.2, w: 8.6, h: 0.75,
    fill: { color: C.dark },
    shadow: mkShadow(),
  });
  s.addText([
    { text: "8 days  ", options: { color: C.red, bold: true, fontSize: 18, fontFace: "Arial Black" } },
    { text: "manual, not reusable  →  ", options: { color: C.slate3, fontSize: 13, fontFace: "Calibri" } },
    { text: "5 minutes  ", options: { color: C.emerald, bold: true, fontSize: 18, fontFace: "Arial Black" } },
    { text: "AI-driven, compounding knowledge", options: { color: C.slate3, fontSize: 13, fontFace: "Calibri" } },
  ], {
    x: 0.7, y: 4.2, w: 8.6, h: 0.75,
    align: "center", valign: "middle", margin: 0,
  });

  addFooter(s, "FORGE AI  ·  R&D Intelligence Platform");
  pageNum(s, 2);
})();

// ============================================================
// SLIDE 3 — THE FORGE AI WAY (Pipeline)
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.dark };

  // Title on dark
  s.addText("The FORGE AI Way", {
    x: 0.7, y: 0.35, w: 8.6, h: 0.55,
    fontSize: 30, fontFace: "Arial Black", color: C.white, margin: 0, bold: true,
  });
  s.addText("One research question in → a complete R&D report out", {
    x: 0.7, y: 0.9, w: 8.6, h: 0.35,
    fontSize: 13, fontFace: "Calibri", color: C.tealL, margin: 0,
  });

  // Pipeline — 5 steps as connected cards
  const steps = [
    { label: "VOC Input", desc: "Describe your\nresearch question", icon: "📝" },
    { label: "AI Search", desc: "6 global patent\nsources scanned", icon: "🌍" },
    { label: "Deep Read", desc: "Full text analysis\nX-Y extraction", icon: "🧬" },
    { label: "AI Analyze", desc: "White space\n+ DOE design", icon: "🎯" },
    { label: "Report", desc: "Complete report\n+ AI slides", icon: "📊" },
  ];

  const stepW = 1.55;
  const gap = 0.2;
  const totalW = steps.length * stepW + (steps.length - 1) * gap;
  const startX = (FW - totalW) / 2;

  steps.forEach((st, i) => {
    const x = startX + i * (stepW + gap);
    const y = 1.6;

    // Card
    card(s, x, y, stepW, 2.5, C.dark2);
    // Teal top accent
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: stepW, h: 0.04, fill: { color: C.teal },
    });

    // Icon
    s.addText(st.icon, {
      x, y: y + 0.2, w: stepW, h: 0.5,
      fontSize: 26, align: "center", margin: 0,
    });
    // Label
    s.addText(st.label, {
      x, y: y + 0.7, w: stepW, h: 0.4,
      fontSize: 13, fontFace: "Arial Black", color: C.white, align: "center", margin: 0, bold: true,
    });
    // Desc
    s.addText(st.desc, {
      x, y: y + 1.2, w: stepW, h: 0.9,
      fontSize: 10, fontFace: "Calibri", color: C.muted, align: "center", margin: 0,
    });

    // Arrow between cards
    if (i < steps.length - 1) {
      s.addText("→", {
        x: x + stepW, y: y + 0.7, w: gap, h: 0.5,
        fontSize: 18, color: C.tealL, align: "center", valign: "middle", margin: 0,
      });
    }
  });

  // Bottom highlight
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 4.55, w: 8.6, h: 0.55,
    fill: { color: C.teal, transparency: 80 },
  });
  s.addText("Knowledge compounds across projects. The more you use it, the smarter it gets.", {
    x: 0.7, y: 4.55, w: 8.6, h: 0.55,
    fontSize: 12, fontFace: "Calibri", color: C.tealL, align: "center", valign: "middle", margin: 0, italic: true,
  });

  darkPageNum(s, 3);
})();

// ============================================================
// SLIDE 4 — GLOBAL PATENT INTELLIGENCE
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.cream };
  addTopBar(s);

  slideTitle(s, "Global Patent Intelligence", "6 sources · full-text deep reading · automatic fallback");

  // Left: 6 sources as cards in 2x3 grid
  const sources = [
    { name: "Google Patents", cover: "Global" },
    { name: "USPTO", cover: "USA" },
    { name: "EPO Espacenet", cover: "Europe" },
    { name: "WIPO Patentscope", cover: "Global PCT" },
    { name: "Google Scholar", cover: "Academic" },
    { name: "DeepSeek LLM", cover: "Training knowledge" },
  ];

  sources.forEach((src, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.7 + col * 2.7;
    const y = 1.45 + row * 0.72;
    card(s, x, y, 2.5, 0.6, C.white);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.06, h: 0.6, fill: { color: C.teal },
    });
    s.addText(src.name, {
      x: x + 0.2, y, w: 1.6, h: 0.6,
      fontSize: 12, fontFace: "Calibri", color: C.dark, valign: "middle", margin: 0, bold: true,
    });
    s.addText(src.cover, {
      x: x + 1.7, y, w: 0.7, h: 0.6,
      fontSize: 8, fontFace: "Calibri", color: C.muted, valign: "middle", align: "right", margin: 0,
    });
  });

  // Right: Key stats
  const rightX = 6.1;
  card(s, rightX, 1.45, 3.2, 1.6, C.white);

  s.addText("Every patent is real", {
    x: rightX + 0.25, y: 1.55, w: 2.8, h: 0.35,
    fontSize: 14, fontFace: "Arial Black", color: C.dark, margin: 0, bold: true,
  });

  const stats = [
    { val: "10,000+", label: "characters extracted\nper patent" },
    { val: "30", label: "patents analyzed\nin ~3 minutes" },
    { val: "6", label: "auto-fallback\nlevels" },
  ];
  stats.forEach((st, i) => {
    const sy = 1.95 + i * 0.5;
    s.addText(st.val, {
      x: rightX + 0.25, y: sy, w: 0.9, h: 0.45,
      fontSize: 18, fontFace: "Arial Black", color: C.teal, margin: 0, bold: true, valign: "middle",
    });
    s.addText(st.label, {
      x: rightX + 1.2, y: sy, w: 1.8, h: 0.45,
      fontSize: 9, fontFace: "Calibri", color: C.body, margin: 0, valign: "middle",
    });
    // Separator
    if (i < stats.length - 1) {
      s.addShape(pres.shapes.RECTANGLE, {
        x: rightX + 0.25, y: sy + 0.48, w: 2.7, h: 0.01, fill: { color: C.slate2 },
      });
    }
  });

  // Bottom: Deep analysis description
  card(s, 0.7, 3.65, 8.6, 1.0, C.white);
  s.addText("Full-Text Deep Analysis", {
    x: 0.9, y: 3.72, w: 4, h: 0.3,
    fontSize: 13, fontFace: "Arial Black", color: C.dark, margin: 0, bold: true,
  });
  s.addText("For each patent: Abstract + Claims + Description — all extracted, parsed, and fed to the LLM. "
    + "No summaries. No truncation. Every claim is citeable.", {
    x: 0.9, y: 4.0, w: 8.2, h: 0.55,
    fontSize: 11, fontFace: "Calibri", color: C.body, margin: 0,
  });

  addFooter(s, "FORGE AI  ·  R&D Intelligence Platform");
  pageNum(s, 4);
})();

// ============================================================
// SLIDE 5 — X-Y EXTRACTION & EVIDENCE GRADING
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.cream };
  addTopBar(s);

  slideTitle(s, "X-Y Extraction & Evidence Grading", "From patent text to structured technical knowledge");

  // Left: What is X-Y
  card(s, 0.7, 1.45, 4.1, 2.5, C.white);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 1.45, w: 4.1, h: 0.04, fill: { color: C.teal },
  });
  s.addText("What Is X → Y?", {
    x: 0.9, y: 1.6, w: 3.7, h: 0.35,
    fontSize: 14, fontFace: "Arial Black", color: C.dark, margin: 0, bold: true,
  });
  s.addText([
    { text: "X", options: { bold: true, color: C.teal } },
    { text: " = material, composition, or\n   process parameter", options: { color: C.body } },
  ], {
    x: 0.9, y: 2.0, w: 3.7, h: 0.55,
    fontSize: 11.5, fontFace: "Calibri", margin: 0,
  });
  s.addText([
    { text: "Y", options: { bold: true, color: C.teal } },
    { text: " = performance or effect", options: { color: C.body } },
  ], {
    x: 0.9, y: 2.55, w: 3.7, h: 0.3,
    fontSize: 11.5, fontFace: "Calibri", margin: 0,
  });
  s.addText("e.g., Adhesion strength increased from\n3.2 → 8.7 N/cm when silane content\nwas raised from 1.5 → 3.0 wt%", {
    x: 0.9, y: 2.95, w: 3.7, h: 0.7,
    fontSize: 10, fontFace: "Calibri", color: C.muted, margin: 0, italic: true,
  });

  // Right: Evidence grading levels
  card(s, 5.2, 1.45, 4.1, 2.5, C.white);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.45, w: 4.1, h: 0.04, fill: { color: C.amber },
  });
  s.addText("6-Level Evidence Grading", {
    x: 5.4, y: 1.6, w: 3.7, h: 0.35,
    fontSize: 14, fontFace: "Arial Black", color: C.dark, margin: 0, bold: true,
  });

  const grades = [
    { label: "Fact", desc: "Patent disclosure", color: C.emerald },
    { label: "Extracted", desc: "AI normalization", color: C.teal },
    { label: "Inferred", desc: "AI inference", color: C.tealL },
    { label: "Hypothesis", desc: "R&D hypothesis", color: C.amber },
    { label: "DOE", desc: "Experiment suggestion", color: "F97316" },
  ];
  grades.forEach((g, i) => {
    const gy = 2.0 + i * 0.35;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 5.4, y: gy + 0.02, w: 0.08, h: 0.24, fill: { color: g.color },
    });
    s.addText(g.label, {
      x: 5.6, y: gy, w: 1.0, h: 0.3,
      fontSize: 10.5, fontFace: "Calibri", color: C.dark, margin: 0, bold: true, valign: "middle",
    });
    s.addText(g.desc, {
      x: 6.5, y: gy, w: 1.6, h: 0.3,
      fontSize: 10, fontFace: "Calibri", color: C.muted, margin: 0, valign: "middle",
    });
  });

  // Bottom: Key rules
  card(s, 0.7, 4.2, 8.6, 0.75, C.dark);
  s.addText([
    { text: "⛓️  ", options: { fontSize: 12 } },
    { text: "Every extraction cites its patent number.  ", options: { color: C.slate3, fontSize: 11, fontFace: "Calibri" } },
    { text: "🔬  ", options: { fontSize: 12 } },
    { text: "Claims ≠ experimental evidence.  ", options: { color: C.slate3, fontSize: 11, fontFace: "Calibri" } },
    { text: "📊  ", options: { fontSize: 12 } },
    { text: "Cross-patent comparison with concrete numbers.", options: { color: C.slate3, fontSize: 11, fontFace: "Calibri" } },
  ], {
    x: 0.7, y: 4.2, w: 8.6, h: 0.75,
    align: "center", valign: "middle", margin: 0,
  });

  addFooter(s, "FORGE AI  ·  R&D Intelligence Platform");
  pageNum(s, 5);
})();

// ============================================================
// SLIDE 6 — COMPETITIVE WHITE SPACE
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.cream };
  addTopBar(s);

  slideTitle(s, "Competitive Intelligence & White Space", "Know where everyone is — and where nobody is looking");

  // 4 capability cards in 2x2
  const caps = [
    { title: "Competitor Products", desc: "Identifies who is working on\nyour problem and what they\nhave achieved so far.", icon: "🏢" },
    { title: "Benchmark Analysis", desc: "Compares performance data\nacross all found solutions\nwith concrete numbers.", icon: "📈" },
    { title: "White Space Mapping", desc: "Finds the gaps — compositions,\nprocesses, and applications\nno patent covers.", icon: "🗺️" },
    { title: "Critical X Ranking", desc: "Ranks which input variables\nactually drive your CTQs.\nTest the right things first.", icon: "🎯" },
  ];

  caps.forEach((cap, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.7 + col * 4.45;
    const y = 1.5 + row * 1.65;
    card(s, x, y, 4.15, 1.45, C.white);
    // Icon circle
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.2, y: y + 0.15, w: 0.5, h: 0.5, fill: { color: C.tealBg },
    });
    s.addText(cap.icon, {
      x: x + 0.2, y: y + 0.15, w: 0.5, h: 0.5,
      fontSize: 16, align: "center", valign: "middle", margin: 0,
    });
    s.addText(cap.title, {
      x: x + 0.85, y: y + 0.15, w: 3.1, h: 0.35,
      fontSize: 14, fontFace: "Arial Black", color: C.dark, margin: 0, bold: true, valign: "middle",
    });
    s.addText(cap.desc, {
      x: x + 0.85, y: y + 0.55, w: 3.1, h: 0.75,
      fontSize: 10.5, fontFace: "Calibri", color: C.body, margin: 0,
    });
  });

  addFooter(s, "FORGE AI  ·  R&D Intelligence Platform");
  pageNum(s, 6);
})();

// ============================================================
// SLIDE 7 — AI-DESIGNED DOE
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.cream };
  addTopBar(s);

  slideTitle(s, "AI-Designed DOE", "From patent evidence to experimental plans — in minutes");

  // Two-column layout
  // Left: 1st DOE
  card(s, 0.7, 1.45, 4.1, 2.5, C.white);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 1.45, w: 4.1, h: 0.04, fill: { color: C.teal },
  });
  s.addText("1st DOE  ·  Screening", {
    x: 0.9, y: 1.6, w: 3.7, h: 0.35,
    fontSize: 15, fontFace: "Arial Black", color: C.dark, margin: 0, bold: true,
  });
  s.addText("Fractional factorial design", {
    x: 0.9, y: 1.95, w: 3.7, h: 0.25,
    fontSize: 11, fontFace: "Calibri", color: C.teal, margin: 0, bold: true,
  });
  const doe1 = [
    "Identifies dominant X variables",
    "Resolution IV — no confounding of main effects",
    "Narrow down from many factors to few",
    "2–3 center points for curvature detection",
  ];
  s.addText(doe1.map((t, i) => ({
    text: t,
    options: { bullet: true, breakLine: i < doe1.length - 1, fontSize: 11, fontFace: "Calibri", color: C.body },
  })), {
    x: 0.9, y: 2.3, w: 3.7, h: 1.45,
    margin: 0, valign: "top",
    paraSpaceAfter: 4,
  });

  // Right: 2nd DOE
  card(s, 5.2, 1.45, 4.1, 2.5, C.white);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.45, w: 4.1, h: 0.04, fill: { color: C.amber },
  });
  s.addText("2nd DOE  ·  Optimization", {
    x: 5.4, y: 1.6, w: 3.7, h: 0.35,
    fontSize: 15, fontFace: "Arial Black", color: C.dark, margin: 0, bold: true,
  });
  s.addText("Central composite design", {
    x: 5.4, y: 1.95, w: 3.7, h: 0.25,
    fontSize: 11, fontFace: "Calibri", color: C.amber, margin: 0, bold: true,
  });
  const doe2 = [
    "Finds the optimal formulation",
    "Response surface modeling",
    "Desirability function — multi-objective",
    "Validated sweet spot confirmation",
  ];
  s.addText(doe2.map((t, i) => ({
    text: t,
    options: { bullet: true, breakLine: i < doe2.length - 1, fontSize: 11, fontFace: "Calibri", color: C.body },
  })), {
    x: 5.4, y: 2.3, w: 3.7, h: 1.45,
    margin: 0, valign: "top",
    paraSpaceAfter: 4,
  });

  // Bottom: Loop visualization
  card(s, 0.7, 4.2, 8.6, 0.65, C.dark);
  s.addText([
    { text: "🧪  You run experiments  →  ", options: { color: C.slate3, fontSize: 11, fontFace: "Calibri" } },
    { text: "🤖  AI analyzes your DOE data  →  ", options: { color: C.tealL, fontSize: 11, fontFace: "Calibri" } },
    { text: "🔄  Model updates. Learning compounds.", options: { color: C.slate3, fontSize: 11, fontFace: "Calibri" } },
  ], {
    x: 0.7, y: 4.2, w: 8.6, h: 0.65,
    align: "center", valign: "middle", margin: 0,
  });

  addFooter(s, "FORGE AI  ·  R&D Intelligence Platform");
  pageNum(s, 7);
})();

// ============================================================
// SLIDE 8 — COMPLETE R&D REPORT
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.cream };
  addTopBar(s);

  slideTitle(s, "Complete R&D Report", "9-step workflow · 3 export formats · AI-designed slides");

  // 9-step workflow as a horizontal flow
  const flowSteps = ["01 Intake", "02 VOC→CTQ", "03 Mining", "04 X-Y Extract", "05 Synthesize", "06 Risk", "07 DOE", "08 Learn", "09 Replicate"];

  // Draw a colored bar for the flow
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 1.55, w: 8.6, h: 0.06, fill: { color: C.teal },
  });

  flowSteps.forEach((st, i) => {
    const x = 0.7 + i * (8.6 / 9);
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.32, y: 1.4, w: 0.35, h: 0.35, fill: { color: C.teal },
    });
    s.addText(`${i + 1}`, {
      x: x + 0.32, y: 1.4, w: 0.35, h: 0.35,
      fontSize: 10, fontFace: "Calibri", color: C.white, align: "center", valign: "middle", margin: 0, bold: true,
    });
    s.addText(st, {
      x: x, y: 1.8, w: 0.95, h: 0.3,
      fontSize: 7, fontFace: "Calibri", color: C.dark, align: "center", margin: 0, bold: true,
    });
  });

  // 3 export format cards
  const formats = [
    { name: "Markdown", ext: ".md", desc: "Plain text — paste into\nNotion, wiki, or docs", icon: "📝" },
    { name: "Word", ext: ".docx", desc: "Formatted document —\nCJK-optimized fonts", icon: "📄" },
    { name: "PowerPoint", ext: ".pptx", desc: "AI-designed slides —\n10 color palettes, premium look", icon: "🎨" },
  ];

  formats.forEach((fmt, i) => {
    const x = 0.7 + i * 3.0;
    const y = 2.5;
    card(s, x, y, 2.7, 1.8, C.white);
    // Teal accent top
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 2.7, h: 0.04, fill: { color: C.teal },
    });
    s.addText(fmt.icon, {
      x, y: y + 0.15, w: 2.7, h: 0.45,
      fontSize: 24, align: "center", margin: 0,
    });
    s.addText(fmt.name, {
      x, y: y + 0.6, w: 2.7, h: 0.35,
      fontSize: 15, fontFace: "Arial Black", color: C.dark, align: "center", margin: 0, bold: true,
    });
    s.addText(fmt.ext, {
      x, y: y + 0.9, w: 2.7, h: 0.25,
      fontSize: 9, fontFace: "Calibri", color: C.teal, align: "center", margin: 0,
    });
    s.addText(fmt.desc, {
      x, y: y + 1.1, w: 2.7, h: 0.55,
      fontSize: 10, fontFace: "Calibri", color: C.body, align: "center", margin: 0,
    });
  });

  // Report contents
  card(s, 0.7, 4.6, 8.6, 0.55, C.dark);
  s.addText("Report includes:  Patent priority scoring  ·  X/Y dictionaries  ·  X-Y relationship matrix  ·  Risk screening  ·  DOE portfolio", {
    x: 0.7, y: 4.6, w: 8.6, h: 0.55,
    fontSize: 10.5, fontFace: "Calibri", color: C.slate3, align: "center", valign: "middle", margin: 0,
  });

  addFooter(s, "FORGE AI  ·  R&D Intelligence Platform");
  pageNum(s, 8);
})();

// ============================================================
// SLIDE 9 — CLOSED-LOOP WITH SPC
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.cream };
  addTopBar(s);

  slideTitle(s, "Closed-Loop R&D: FORGE AI + SPC Platform", "From literature to production — a unified learning system");

  // Four-step cycle as horizontal flow
  const loopSteps = [
    { num: "1", title: "FORGE AI", desc: "Patent intelligence\nX-Y extraction\nInitial DOE design", color: C.teal },
    { num: "2", title: "You Run", desc: "Experiments in\nthe lab or pilot plant", color: C.amber },
    { num: "3", title: "SPC Platform", desc: "Statistical analysis\nResponse surfaces\nDesirability optimization", color: C.teal },
    { num: "4", title: "FORGE AI", desc: "Refines the model\n2nd-round DOE\nKnowledge compounds", color: C.teal },
  ];

  loopSteps.forEach((st, i) => {
    const x = 0.7 + i * 2.3;
    const y = 1.5;
    card(s, x, y, 2.0, 1.7, C.white);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 2.0, h: 0.04, fill: { color: st.color },
    });
    // Number circle
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.1, y: y + 0.15, w: 0.35, h: 0.35, fill: { color: st.color },
    });
    s.addText(st.num, {
      x: x + 0.1, y: y + 0.15, w: 0.35, h: 0.35,
      fontSize: 14, fontFace: "Arial Black", color: C.white, align: "center", valign: "middle", margin: 0, bold: true,
    });
    s.addText(st.title, {
      x: x + 0.55, y: y + 0.15, w: 1.35, h: 0.35,
      fontSize: 13, fontFace: "Arial Black", color: C.dark, margin: 0, bold: true, valign: "middle",
    });
    s.addText(st.desc, {
      x: x + 0.2, y: y + 0.6, w: 1.6, h: 0.95,
      fontSize: 10, fontFace: "Calibri", color: C.body, margin: 0,
    });
    // Arrow between cards
    if (i < loopSteps.length - 1) {
      s.addText("→", {
        x: x + 2.0, y: y + 0.5, w: 0.3, h: 0.5,
        fontSize: 20, color: C.tealL, align: "center", valign: "middle", margin: 0,
      });
    }
  });

  // Curved loop-back arrow (text)
  s.addText("↻  Learning loop — each cycle makes the model smarter", {
    x: 2, y: 3.35, w: 6, h: 0.35,
    fontSize: 11, fontFace: "Calibri", color: C.teal, align: "center", margin: 0, italic: true,
  });

  // Bottom integration note
  card(s, 0.7, 4.0, 8.6, 0.45, C.dark);
  s.addText([
    { text: "FORGE AI ", options: { color: C.tealL, bold: true, fontSize: 11, fontFace: "Calibri" } },
    { text: "tells you ", options: { color: C.slate3, fontSize: 11, fontFace: "Calibri" } },
    { text: "what to test and why.", options: { color: C.white, fontSize: 11, fontFace: "Calibri" } },
    { text: "   SPC Platform ", options: { color: C.tealL, bold: true, fontSize: 11, fontFace: "Calibri" } },
    { text: "tells you ", options: { color: C.slate3, fontSize: 11, fontFace: "Calibri" } },
    { text: "what happened.", options: { color: C.white, fontSize: 11, fontFace: "Calibri" } },
  ], {
    x: 0.7, y: 4.0, w: 8.6, h: 0.45,
    align: "center", valign: "middle", margin: 0,
  });

  addFooter(s, "FORGE AI  ·  R&D Intelligence Platform");
  pageNum(s, 9);
})();

// ============================================================
// SLIDE 10 — GET STARTED
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.dark };

  // Decorative shapes
  s.addShape(pres.shapes.RECTANGLE, {
    x: -1, y: 3.5, w: 5, h: 3.5, fill: { color: C.teal, transparency: 92 }, rotate: -10,
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6, y: -1, w: 5, h: 3.5, fill: { color: C.tealL, transparency: 94 }, rotate: 15,
  });

  // Title
  s.addText("Start Your Project", {
    x: 0.7, y: 0.5, w: 8.6, h: 0.6,
    fontSize: 34, fontFace: "Arial Black", color: C.white, margin: 0, bold: true,
  });
  s.addText("From university lab to R&D floor — FORGE AI works at every scale.", {
    x: 0.7, y: 1.1, w: 8.6, h: 0.35,
    fontSize: 13, fontFace: "Calibri", color: C.tealL, margin: 0,
  });

  // 3 steps
  const steps = [
    { num: "1", title: "Describe Your VOC", desc: "Enter your research question —\nthe more specific, the better." },
    { num: "2", title: "AI Does the Work", desc: "Searches, reads, extracts, and\nanalyzes 30+ patents in minutes." },
    { num: "3", title: "Get Your Report", desc: "Complete R&D report + AI-\ndesigned slides in one click." },
  ];

  steps.forEach((st, i) => {
    const x = 0.7 + i * 3.0;
    const y = 1.8;
    card(s, x, y, 2.7, 2.0, C.dark2);
    // Number circle
    s.addShape(pres.shapes.OVAL, {
      x: x + 1.0, y: y + 0.15, w: 0.6, h: 0.6, fill: { color: C.teal },
    });
    s.addText(st.num, {
      x: x + 1.0, y: y + 0.15, w: 0.6, h: 0.6,
      fontSize: 20, fontFace: "Arial Black", color: C.white, align: "center", valign: "middle", margin: 0, bold: true,
    });
    s.addText(st.title, {
      x: x + 0.2, y: y + 0.9, w: 2.3, h: 0.35,
      fontSize: 14, fontFace: "Arial Black", color: C.white, align: "center", margin: 0, bold: true,
    });
    s.addText(st.desc, {
      x: x + 0.2, y: y + 1.25, w: 2.3, h: 0.6,
      fontSize: 10, fontFace: "Calibri", color: C.muted, align: "center", margin: 0,
    });
  });

  // CTA bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 4.3, w: 8.6, h: 0.65,
    fill: { color: C.teal },
    shadow: mkShadow(),
  });
  s.addText("⚒️  Try FORGE AI Live  →  ai-chemist.zeabur.app", {
    x: 0.7, y: 4.3, w: 8.6, h: 0.65,
    fontSize: 16, fontFace: "Arial Black", color: C.white, align: "center", valign: "middle", margin: 0, bold: true,
  });

  // Bottom links
  s.addText("GitHub: github.com/newbison/AI_CHEMIST  ·  Built with DeepSeek + FastAPI + React + Docker", {
    x: 0.7, y: 5.0, w: 8.6, h: 0.35,
    fontSize: 9, fontFace: "Calibri", color: C.muted, align: "center", margin: 0,
  });

  darkPageNum(s, 10);
})();

// ============================================================
// WRITE
// ============================================================
const OUTPUT = __dirname + "/FORGE_AI_Introduction_Deck.pptx";
pres.writeFile({ fileName: OUTPUT }).then(() => {
  console.log("✅ Written to", OUTPUT);
  console.log("File size:", fs.statSync(OUTPUT).size, "bytes");
}).catch(err => {
  console.error("❌ Error:", err.message);
  process.exit(1);
});
