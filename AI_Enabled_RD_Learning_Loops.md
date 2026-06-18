# AI-Enabled R&D Learning Loop

**Purpose:** Capture the full R&D workflow discussed: from Voice of Customer (VOC) intake to patent intelligence, experiment design, lab execution, post-experiment learning, and knowledge-base update.

**Intended audience:** R&D scientists, product engineers, technical managers, AI/app developers, patent/IP partners, regulatory partners, and business stakeholders.

**Core idea:**

> Convert ambiguous customer needs into measurable technical requirements, use internal and external evidence to design experiments, and turn every experiment into reusable organizational knowledge.

---

# 1. Executive Summary

A traditional R&D process often follows this path:

```text
VOC from business team
    ↓
R&D verifies VOC
    ↓
Translate VOC into technical specifications
    ↓
Search patent databases
    ↓
Identify top companies
    ↓
Select most relevant patents
    ↓
Extract DOE, input Xs, output Ys, and X-Y relationships
    ↓
Design initial experiments
```

In the AI era, this can be upgraded into a closed-loop R&D intelligence system:

```text
VOC
 → Business validation
 → CTQ translation
 → Evidence mining
     internal data + patents + products + literature
 → Technical synthesis
     X/Y relationships + tradeoffs + white space
 → Feasibility screening
     IP + regulatory + manufacturing + supplier + risk
 → DOE design
 → Lab execution
 → Data analysis
 → Post-experiment learning
 → Knowledge base update
 → Next experiment recommendation
```

The system should not be only a patent summarizer. The higher-value goal is:

> Build an AI-assisted R&D operating loop that continuously converts evidence into hypotheses, experiments, learnings, design rules, and next actions.

---

# 2. High-Level Loop Overview

## 2.1 Full R&D Loop

```text
1. VOC intake
2. Business validation
3. VOC-to-CTQ translation
4. Regulatory / claim feasibility screen
5. Internal knowledge mining
6. Commercial benchmark analysis
7. Patent landscape search
8. Top company and patent ranking
9. Patent DOE / X-Y extraction
10. Test method normalization
11. Cross-patent X-Y synthesis
12. White-space and design-around analysis
13. Manufacturability and supplier feasibility check
14. Risk management mapping
15. Experiment portfolio prioritization
16. DOE statistical design
17. Lab protocol and sample plan generation
18. Experiment execution and data capture
19. Statistical analysis and post-experiment learning
20. Knowledge base update
21. Next-round experiment recommendation
```

## 2.2 Simplified Executive Loop

```text
Customer Need
    ↓
Business + Technical Translation
    ↓
Evidence Mining
    ↓
Hypothesis Generation
    ↓
Experiment Design
    ↓
Experiment Execution
    ↓
Learning Extraction
    ↓
Knowledge Update
    ↓
Next Decision
```

## 2.3 Mandatory Human Review Gates

For a Fortune 500 materials or medical device company, AI should accelerate the process but not replace technical accountability.

```text
Gate 1 — Business confirms VOC interpretation
Gate 2 — R&D confirms CTQs and test methods
Gate 3 — IP/legal reviews patent risk signals
Gate 4 — Regulatory reviews claim feasibility
Gate 5 — Manufacturing reviews feasibility
Gate 6 — Scientist validates extracted X-Y relationships
Gate 7 — Lab team reviews DOE feasibility
Gate 8 — Scientist approves post-experiment learning record
Gate 9 — Project team approves next-round recommendation
```

---

# 3. Loop 1 — VOC Intake and Clarification

## 3.1 Objective

Capture the original customer or market need and convert it into a structured problem statement.

The key challenge is that VOC is usually ambiguous. Business language often sounds like:

```text
Customer wants a more breathable, skin-friendly, long-wear adhesive dressing with less pain on removal.
```

R&D needs to translate this into measurable technical questions.

## 3.2 Inputs

- Original VOC statement
- Customer segment
- Use environment
- Target product category
- Competitor reference product, if known
- Business priority
- Known complaints or unmet needs
- Geographic market
- Expected launch timing

## 3.3 AI Tasks

The AI should:

1. Preserve the original VOC wording.
2. Extract implied customer needs.
3. Identify ambiguous terms.
4. Generate clarification questions.
5. Translate customer language into candidate technical attributes.
6. Identify potential contradictions among requirements.

## 3.4 Example Output

```markdown
# VOC Translation Brief

## Original VOC
Customer wants a more breathable, skin-friendly, long-wear adhesive dressing with less pain on removal.

## Interpreted Customer Needs
1. Improved moisture vapor transmission
2. Reduced skin trauma during removal
3. Longer wear time
4. Stable adhesion under sweating and body movement
5. Low irritation risk

## Ambiguous Terms
- "Breathable" may refer to MVTR, air permeability, comfort, or reduced maceration.
- "Skin-friendly" may refer to irritation, sensitization, pain, skin stripping, or residue.
- "Long-wear" may mean 3 days, 7 days, 14 days, or another duration.

## Clarifying Questions
1. What patient or user segment raised this need?
2. What current product is considered inadequate?
3. What is the minimum acceptable wear duration?
4. What test method should define breathability?
5. Is "less pain" a marketing claim, clinical claim, or internal design target?
```

## 3.5 Important Design Principle

Do not immediately jump from VOC to solution. First convert VOC into a testable problem.

---

# 4. Loop 2 — Business and Market Validation

## 4.1 Objective

Determine whether the VOC is commercially meaningful enough to justify R&D investment.

A technically interesting problem may not be a business priority. This loop prevents R&D from optimizing for weak or isolated customer signals.

## 4.2 Key Questions

```text
1. Is this VOC from one customer or repeated across multiple customers?
2. Which customer segment does it represent?
3. What is the economic value of solving it?
4. Is there a price premium, share gain, or retention value?
5. Which competitor product is setting the expectation?
6. Is the VOC a must-have requirement or a nice-to-have?
7. Is the need urgent enough to affect the product roadmap?
```

## 4.3 Output

```markdown
# Business Validation Scorecard

| Dimension | Assessment | Confidence | Notes |
|---|---|---:|---|
| Customer pain exists | High | 85% | Repeated in sales notes and complaints |
| Market value | Medium | 65% | Relevant to premium segment |
| Strategic fit | High | 80% | Aligns with wound care growth platform |
| Differentiation potential | Medium | 60% | Competitors already claim gentle removal |
| R&D urgency | Medium | 70% | Could support next-generation platform |
```

## 4.4 Human Review Gate

Business and R&D should align on whether the VOC deserves technical exploration before deep patent or DOE work begins.

---

# 5. Loop 3 — VOC-to-CTQ Translation

## 5.1 Objective

Convert customer needs into Critical-to-Quality attributes, measurable technical metrics, and possible test methods.

## 5.2 Definitions

- **VOC:** Voice of Customer; what the customer says they want.
- **CTQ:** Critical to Quality; measurable technical characteristics that determine whether the need is met.
- **Y response:** Output metric measured in testing.
- **X variable:** Input factor that may affect a Y response.

## 5.3 Example CTQ Matrix

```markdown
| Customer Need | Technical Attribute | Candidate Metric | Test Method | Initial Target | Risk |
|---|---|---|---|---|---|
| More breathable | Moisture vapor transport | MVTR | Internal or standard MVTR method | Higher than benchmark | May reduce adhesion |
| Gentle removal | Lower skin trauma | Peel force, skin stripping, pain score | 180° peel, skin mimic, clinical simulation | Lower than benchmark | May reduce securement |
| Long wear | Adhesion durability | Edge lift, shear, wear simulation | Internal wear model | 7-day wear target | Irritation risk |
| No residue | Cohesive stability | Residue rating | Visual or gravimetric method | Minimal residue | Formulation-dependent |
| Comfortable | Conformability | Bending stiffness, thickness | Internal mechanical method | Better than benchmark | Durability risk |
```

## 5.4 AI Tasks

The AI should:

1. Generate the CTQ matrix.
2. Suggest measurable Y responses.
3. Suggest possible X variables.
4. Identify tradeoffs.
5. Identify claim and regulatory implications.
6. Flag missing test methods.

## 5.5 Example Tradeoff Map

```text
Higher adhesion may improve wear time but increase pain on removal.
Higher MVTR may improve breathability but reduce occlusiveness.
Lower coat weight may reduce trauma but increase edge lift.
Higher crosslinking may reduce residue but alter tack and peel behavior.
Thinner backing film may improve conformability but reduce handling robustness.
```

---

# 6. Loop 4 — Regulatory and Claim Feasibility Screen

## 6.1 Objective

Check whether intended product claims are technically and regulatorily supportable.

This is especially important for medical devices, where claims such as "gentle," "atraumatic," "skin-friendly," "antimicrobial," or "reduces infection" may require different evidence levels.

## 6.2 AI Tasks

The AI should:

1. Identify explicit and implied claims in the VOC.
2. Separate internal design targets from external marketing claims.
3. Suggest evidence required to support each claim.
4. Flag high-risk claims.
5. Recommend early regulatory review where needed.

## 6.3 Example Output

```markdown
# Claim Feasibility Matrix

| Intended Claim | Technical Metric | Evidence Needed | Regulatory / Claim Risk |
|---|---|---|---|
| Breathable | MVTR | Bench MVTR data vs benchmark | Low to Medium |
| Gentle removal | Peel, skin stripping, pain score | Bench and possibly simulated-use data | Medium |
| Skin-friendly | Irritation, sensitization, skin trauma | Biocompatibility and clinical/simulated data | Medium to High |
| Reduces infection risk | Microbial or clinical endpoint | Strong clinical evidence likely required | High |
```

## 6.4 Human Review Gate

Regulatory and claims partners should review the claim matrix before the DOE is finalized.

---

# 7. Loop 5 — Internal Knowledge Mining

## 7.1 Objective

Search internal company knowledge before investing in new external research or experiments.

In a large materials company, internal data may be more valuable than patent data because it contains real experiments, failures, process details, and product constraints.

## 7.2 Internal Sources

- Old project reports
- Failed experiments
- Lab notebooks
- Formulation databases
- Complaint investigations
- Technical service reports
- Manufacturing deviation reports
- Regulatory submissions
- Prior DOE results
- Internal test method reports
- Supplier qualification documents

## 7.3 Key Questions

```text
1. Have we tried this before?
2. What worked?
3. What failed?
4. Why did it fail?
5. Which material systems were tested?
6. Which test methods were used?
7. Were results comparable to current needs?
8. Are there existing raw materials or platforms we can reuse?
```

## 7.4 Output

```markdown
# Internal Knowledge Summary

## Relevant Prior Work
- Project A tested low coat weight acrylic PSA for breathable dressing.
- Project B tested silicone adhesive for gentle removal.
- Report C showed residue increase at low crosslinker levels.

## Reusable Assets
- Existing MVTR method
- Existing skin mimic peel method
- Approved backing film platform
- Qualified acrylic adhesive supplier

## Known Failure Modes
- Edge lift under sweat challenge
- Residue after aging
- Film wrinkling during converting
```

## 7.5 Design Principle

The system should prevent repeated failure. A good AI R&D system should remember not only successes, but also failed paths and why they failed.

---

# 8. Loop 6 — Commercial Benchmark Analysis

## 8.1 Objective

Analyze actual commercial products, not only patents.

Patents show what competitors disclosed. Products show what competitors commercialized.

## 8.2 Sources

- Product datasheets
- Instructions for use
- Packaging claims
- Product websites
- Clinical or technical brochures
- Public regulatory summaries, where available
- Competitive teardown data
- Customer feedback
- Sales intelligence

## 8.3 AI Tasks

The AI should:

1. Extract competitor claims.
2. Map claims to likely technical mechanisms.
3. Identify disclosed materials or structures.
4. Compare claimed performance across products.
5. Identify commercial gaps.
6. Link benchmark claims to CTQs.

## 8.4 Example Output

```markdown
# Commercial Benchmark Matrix

| Product | Company | Claimed Benefit | Likely Technical Mechanism | Evidence Source | Gap |
|---|---|---|---|---|---|
| Product A | Competitor 1 | 7-day wear | Strong adhesive plus breathable film | Datasheet | No pain data disclosed |
| Product B | Competitor 2 | Gentle removal | Silicone adhesive | IFU / marketing claim | Potential lower securement |
| Product C | Competitor 3 | Breathable | High-MVTR film | Technical brochure | Adhesive system unclear |
```

## 8.5 Design Principle

Patent intelligence and commercial benchmark intelligence should be combined. Neither is complete alone.

---

# 9. Loop 7 — Patent Landscape Search

## 9.1 Objective

Identify relevant companies, patents, technology clusters, and experimental disclosures that may inform R&D direction.

## 9.2 Search Dimensions

Search should include:

- Keywords from VOC
- Technical synonyms
- Product category terms
- Material terms
- Function terms
- IPC/CPC classes
- Assignee names
- Claim language
- Experimental method terms

## 9.3 Example Search Strategy

```text
Core concept:
gentle long-wear breathable medical adhesive dressing

Keyword groups:
1. medical adhesive dressing
2. pressure sensitive adhesive
3. silicone adhesive
4. acrylic adhesive
5. breathable film
6. moisture vapor transmission
7. atraumatic removal
8. low trauma
9. skin-friendly
10. long wear
11. edge lift
12. residue
```

## 9.4 Company Ranking Criteria

Top companies should not be selected by patent count alone. Ranking should consider:

```text
Company relevance score =
patent count
+ recent filing activity
+ citation impact
+ product-market relevance
+ claim overlap with VOC
+ number of experimental examples
+ known commercial presence
+ technical transferability
```

## 9.5 Output

```markdown
# Patent Search Protocol

## Search Intent
Identify patents related to breathable, gentle-removal, long-wear adhesive medical dressings.

## Inclusion Criteria
- Medical dressing or skin-contact adhesive article
- Mentions breathability, MVTR, atraumatic removal, long wear, or skin trauma reduction
- Contains experimental data or formulation examples
- Relevant to target material platform

## Exclusion Criteria
- Non-medical labels or tapes unless transferable
- Patents with no experimental examples
- Pure packaging/device design with limited material relevance
```

---

# 10. Loop 8 — Patent Relevance Ranking

## 10.1 Objective

From patents associated with top companies, select the most technically relevant patents for deep analysis.

## 10.2 Patent Relevance Score

```text
Patent relevance score =
VOC semantic match
+ CTQ metric match
+ material-system match
+ claim overlap
+ experimental data richness
+ DOE usefulness
+ transferability to current platform
+ possible IP risk signal
```

## 10.3 Output

```markdown
# Top Patent Shortlist

| Rank | Patent | Assignee | Why Relevant | Data Richness | Transferability |
|---:|---|---|---|---:|---:|
| 1 | Patent 1 | Company A | Breathable PSA dressing with MVTR data | High | High |
| 2 | Patent 2 | Company B | Gentle removal silicone adhesive construction | Medium | High |
| 3 | Patent 3 | Company C | Multi-layer film/adhesive structure | High | Medium |
```

## 10.4 Design Principle

The shortlist should explain why each patent was included. Relevance scoring must be transparent and editable by a scientist.

---

# 11. Loop 9 — Patent DOE, X, Y, and Correlation Extraction

## 11.1 Objective

Extract structured technical intelligence from each patent.

This is the heart of the AI workflow.

## 11.2 For Each Patent, Extract

- Problem addressed
- Product construction
- Material system
- Key claims
- Experimental examples
- Design of experiments
- Input X variables
- Output Y responses
- Test methods
- Units
- Ranges
- Controls
- X-Y relationships
- AI-inferred mechanisms
- Limitations
- Potential design-around ideas

## 11.3 DOE Extraction Template

```markdown
# Patent Technical Extraction Card

## Patent Metadata
- Patent number:
- Assignee:
- Publication date:
- Jurisdiction:
- Status, if known:

## Technical Purpose
Short description of the problem the patent attempts to solve.

## Product / Material Structure
- Backing:
- Adhesive:
- Liner:
- Additives:
- Coating pattern:
- Sterilization or processing, if disclosed:

## Experimental Design
- Experimental objective:
- Formulation variables:
- Process variables:
- Structural variables:
- Controls:
- Sample size:
- Test methods:

## Input X Variables
- X1:
- X2:
- X3:

## Output Y Responses
- Y1:
- Y2:
- Y3:

## X-Y Relationships
- Relationship 1:
- Relationship 2:
- Relationship 3:

## Evidence Type
- Direct patent-disclosed fact
- AI extraction
- AI inference
- R&D recommendation

## Confidence
- High / Medium / Low

## Limitations
- Missing test method details
- Limited examples
- Non-comparable conditions
- Broad claim language
```

## 11.4 Fact vs Inference Separation

The system must clearly separate:

```text
Patent-disclosed fact
vs.
AI-extracted structure
vs.
AI-inferred relationship
vs.
R&D recommendation
```

Example:

```markdown
Fact:
Patent Example 3 discloses adhesive coat weight of 40 gsm and peel adhesion of 2.1 N/25 mm.

Extraction:
Adhesive coat weight is an input X. Peel adhesion is an output Y.

Inference:
Increasing coat weight may increase peel adhesion.

Recommendation:
Include coat weight as a DOE factor.

Confidence:
Medium, because only limited examples are disclosed.
```

---

# 12. Loop 10 — Test Method Normalization

## 12.1 Objective

Normalize output Y metrics across patents, internal reports, and benchmark products.

This is necessary because different sources may use different test conditions.

## 12.2 Common Problems

Different sources may use:

- Different peel angles
- Different substrates
- Different dwell times
- Different humidity conditions
- Different MVTR methods
- Different units
- Different sample preparation methods
- Different aging conditions

## 12.3 Output

```markdown
# Test Method Comparability Matrix

| Metric | Source Method | Internal Method | Comparable? | Concern |
|---|---|---|---|---|
| Peel adhesion | 180° peel on steel | 180° peel on skin mimic | Partial | Substrate difference |
| MVTR | Upright cup | Inverted cup | No | Different moisture gradient |
| Wear time | Human wear | Simulated wear | Partial | Need validation |
| Residue | Visual scale | Gravimetric method | Partial | Scale mismatch |
```

## 12.4 Design Principle

Do not compare numbers blindly. First compare methods.

---

# 13. Loop 11 — Cross-Patent X-Y Synthesis

## 13.1 Objective

Synthesize extracted patent evidence into a cross-patent relationship map.

## 13.2 Output

```markdown
# Cross-Patent X-Y Matrix

| X Variable | Patents Mentioned | Related Y | Direction | Confidence | Recommended Action |
|---|---:|---|---|---:|---|
| Adhesive coat weight | 9 | Peel, MVTR | + peel, - MVTR | High | Include in DOE |
| Crosslinker level | 6 | Residue, cohesion | - residue, + cohesion | Medium | Screen carefully |
| Film thickness | 7 | MVTR, conformability | - MVTR, - conformability | Medium | Include as structural variable |
| Silicone content | 5 | Pain, peel, edge lift | - pain, possible - peel | Medium | Explore with controls |
```

## 13.3 Contradiction Handling

The system should explicitly flag contradictions.

```markdown
# Contradiction Example

Prior evidence:
Patent A suggests higher coat weight reduces MVTR.

Other evidence:
Patent B shows MVTR mostly controlled by backing film permeability.

Possible explanations:
1. Different backing films
2. Different adhesive chemistry
3. Different coat weight range
4. Different MVTR method
5. Different sample conditioning

Recommended action:
Design DOE that isolates coat weight and backing film permeability.
```

---

# 14. Loop 12 — White-Space and Design-Around Analysis

## 14.1 Objective

Identify where competitors are crowded and where technical opportunities may exist.

## 14.2 Key Questions

```text
1. Which X variables are heavily patented?
2. Which output metrics are underexplored?
3. Which material combinations are rarely disclosed?
4. Which performance tradeoffs remain unsolved?
5. Which claims are broad and potentially risky?
6. Which regions or applications have fewer filings?
7. Which design-around paths may be technically plausible?
```

## 14.3 Output

```markdown
# White-Space Analysis

## Crowded Areas
- Silicone adhesive for gentle removal
- Breathable film backing
- Low-trauma dressing construction

## Potential White Space
- Hybrid adhesive systems with controlled removal force
- Pattern-coated structures balancing MVTR and wear time
- Backing film microstructure optimization
- Test-method-backed comfort claims

## Design-Around Ideas
- Different adhesive chemistry
- Different coating pattern
- Different layer sequence
- Different performance target combination
- Different use-case positioning
```

## 14.4 IP Disclaimer

The AI system should not provide legal freedom-to-operate conclusions. It can flag potential concerns for IP counsel review.

---

# 15. Loop 13 — IP / Freedom-to-Operate Pre-Screen

## 15.1 Objective

Identify patent risk signals before experiments are finalized.

## 15.2 Important Distinction

```text
Patent relevance ≠ freedom to operate
```

A relevant patent may be expired, abandoned, narrow, broad, active only in some countries, or easy/hard to design around.

## 15.3 Output

```markdown
# IP Risk Pre-Screen

| Patent | Status | Claim Breadth | Overlap With Proposed Design | Risk Signal | Legal Review Needed |
|---|---|---|---|---|---|
| Patent A | Active | Broad | High | High | Yes |
| Patent B | Expired | Medium | High | Low | Maybe |
| Patent C | Active | Narrow | Medium | Medium | Yes |
```

## 15.4 Human Review Gate

IP/legal must review high-risk signals before final DOE or product development decisions.

---

# 16. Loop 14 — Manufacturability and Supplier Feasibility

## 16.1 Objective

Check whether proposed experiment concepts are practical for current or future manufacturing.

## 16.2 Manufacturing Questions

```text
1. Can current coating equipment achieve the proposed coat weight?
2. Can drying or curing conditions be achieved on current lines?
3. Does the design require new tooling or coating pattern capability?
4. Can the structure survive converting, packaging, and sterilization?
5. Does it introduce new quality control challenges?
6. Can lab-scale results translate to pilot scale?
```

## 16.3 Supplier Questions

```text
1. Is the raw material commercially available?
2. Is it medical grade or suitable for intended use?
3. Are regulatory documents available?
4. Is there dual sourcing?
5. What is the cost risk?
6. What is the supply continuity risk?
7. Is sterilization compatibility known?
8. Are extractables/leachables concerns expected?
```

## 16.4 Output

```markdown
# Feasibility Matrix

| Proposed Design | Lab Feasible | Manufacturing Feasible | Supplier Risk | Key Constraint |
|---|---:|---:|---:|---|
| Pattern-coated adhesive | High | Medium | Low | Requires coating pattern capability |
| New silicone adhesive | Medium | Low to Medium | Medium | Supplier qualification needed |
| Thinner backing film | High | Medium | Low | Wrinkling and converting risk |
```

---

# 17. Loop 15 — Risk Management Mapping

## 17.1 Objective

Connect technical choices to possible product failure modes and user harms.

For medical device development, design choices should be linked to risk thinking early.

## 17.2 Output

```markdown
# Design Risk Mapping

| Design Change | Potential Failure Mode | Potential Harm | Risk Control | Verification Test |
|---|---|---|---|---|
| Lower adhesive coat weight | Edge lift | Device detachment | Minimum peel / wear requirement | Wear simulation |
| Higher tack | Skin trauma | MARSI / pain | Removal force limit | Peel and skin stripping |
| Higher MVTR film | Fluid leakage | Dressing failure | Fluid handling requirement | Leakage / absorbency test |
| Lower crosslinker | Residue | Skin contamination or discomfort | Minimum cohesion requirement | Residue and aging test |
```

## 17.3 Design Principle

Every important X variable should be connected to possible benefits and possible failure modes.

---

# 18. Loop 16 — Experiment Portfolio Prioritization

## 18.1 Objective

Rank proposed experiments before lab execution.

Generating five experiments is not enough. The system should recommend which experiments to run first and why.

## 18.2 Prioritization Criteria

- Learning value
- Probability of success
- Technical risk
- IP risk
- Regulatory burden
- Cost
- Speed
- Platform fit
- Business impact
- Manufacturing feasibility

## 18.3 Output

```markdown
# Experiment Portfolio Matrix

| Experiment | Learning Value | Feasibility | Cost | IP Risk | Business Impact | Priority |
|---|---:|---:|---:|---:|---:|---:|
| Coat weight × crosslinker | High | High | Low | Low | Medium | 1 |
| Silicone/acrylic hybrid | High | Medium | Medium | Medium | High | 2 |
| Backing film thickness | Medium | Medium | High | Low | High | 3 |
| Pattern-coated adhesive | High | Medium | Medium | Medium | High | 4 |
| Sweat challenge wear study | Medium | High | Medium | Low | Medium | 5 |
```

---

# 19. Loop 17 — DOE Statistical Design

## 19.1 Objective

Convert experiment concepts into statistically useful DOE plans.

## 19.2 Required DOE Elements

Each experiment should define:

```text
1. Hypothesis
2. Factors
3. Factor levels
4. Responses
5. Controls
6. Replicates
7. Randomization
8. Blocking factors
9. Acceptance criteria
10. Go/no-go decision rule
11. Expected interactions
12. Minimum detectable effect, if known
13. Known test method variation
```

## 19.3 Example DOE Plan

```markdown
# Experiment 1 — Adhesive Coat Weight × Crosslinker Optimization

## Hypothesis
Reducing adhesive coat weight can improve breathability while maintaining acceptable peel adhesion if cohesive strength is controlled by crosslinker level.

## Factors
- X1: Adhesive coat weight: 25, 40, 55 gsm
- X2: Crosslinker level: 0.2%, 0.5%, 0.8%

## Responses
- Y1: Peel adhesion, N/25 mm
- Y2: MVTR, g/m²/24h
- Y3: Residue score
- Y4: Edge lift after wear simulation

## Controls
- Current commercial or internal baseline construction
- Benchmark competitor product if available

## Decision Rule
Advance formulations with peel adhesion within target range, MVTR above minimum threshold, residue score ≤ 1, and acceptable edge lift.
```

---

# 20. Loop 18 — Lab Protocol and Sample Plan Generation

## 20.1 Objective

Turn DOE design into executable lab instructions.

## 20.2 Outputs

The system should generate:

- Sample matrix
- Sample ID convention
- Randomization table
- Material preparation instructions
- Coating or processing instructions
- Conditioning requirements
- Test request forms
- Data entry templates
- Deviation log
- Safety notes
- Required approvals

## 20.3 Sample ID Design

A good sample ID should encode project, experiment, batch, and condition without becoming too long.

Example:

```text
BRD-EXP001-CW40-XL05-R2
```

Meaning:

```text
BRD = breathable dressing project
EXP001 = experiment 001
CW40 = coat weight 40 gsm
XL05 = crosslinker 0.5%
R2 = replicate 2
```

---

# 21. Loop 19 — Experiment Execution and Data Capture

## 21.1 Objective

Capture raw data and metadata in a structured, analyzable format.

## 21.2 Required Data Capture

- Experiment ID
- Sample ID
- Material lot
- Operator
- Equipment
- Process conditions
- Test method version
- Environmental conditions
- Raw Y values
- Replicate number
- Deviations from protocol
- Observational notes

## 21.3 Data Quality Checks

The app should check:

```text
1. Are all planned samples included?
2. Are all output Ys measured?
3. Are units consistent?
4. Are there missing values?
5. Were test methods changed?
6. Are replicate counts sufficient?
7. Are there obvious outliers?
8. Are deviations documented?
```

---

# 22. Loop 20 — Post-Experiment Learning

## 22.1 Objective

Turn experiment results into reusable knowledge.

The most important mindset shift is:

> Do not treat an experiment as only pass/fail. Treat it as a structured learning event.

## 22.2 Core Questions

Post-experiment learning should answer:

```text
1. What did we expect to happen?
2. What actually happened?
3. Which input Xs significantly affected output Ys?
4. Which patent-derived assumptions were confirmed or contradicted?
5. What technical tradeoffs became clearer?
6. What should we do next?
```

## 22.3 Pre-Experiment Learning Object

Before running the experiment, capture:

```json
{
  "experiment_id": "EXP-2026-001",
  "project": "Breathable gentle-removal dressing",
  "hypothesis": "Lower adhesive coat weight improves MVTR but may reduce peel adhesion.",
  "input_factors": [
    {
      "name": "adhesive_coat_weight",
      "unit": "gsm",
      "levels": [25, 40, 55]
    },
    {
      "name": "crosslinker_level",
      "unit": "%",
      "levels": [0.2, 0.5, 0.8]
    }
  ],
  "output_responses": [
    {
      "name": "peel_adhesion",
      "unit": "N/25mm",
      "target_direction": "within_range",
      "target_range": [1.0, 2.5]
    },
    {
      "name": "MVTR",
      "unit": "g/m2/24h",
      "target_direction": "higher_better",
      "minimum_target": 800
    }
  ],
  "expected_relationships": [
    {
      "x": "adhesive_coat_weight",
      "y": "peel_adhesion",
      "expected_direction": "positive",
      "confidence_before": "high"
    },
    {
      "x": "adhesive_coat_weight",
      "y": "MVTR",
      "expected_direction": "negative",
      "confidence_before": "medium"
    }
  ]
}
```

## 22.4 Post-Experiment Learning Object

After results are available, append:

```json
{
  "experiment_id": "EXP-2026-001",
  "results_summary": {
    "status": "completed",
    "main_findings": [
      "Adhesive coat weight significantly increased peel adhesion.",
      "Crosslinker level significantly reduced residue.",
      "MVTR was not significantly affected within tested coat weight range."
    ]
  },
  "hypothesis_evaluation": [
    {
      "hypothesis": "Coat weight increases peel adhesion",
      "result": "confirmed"
    },
    {
      "hypothesis": "Coat weight reduces MVTR",
      "result": "not_supported_in_tested_range"
    }
  ],
  "recommended_next_steps": [
    "Keep coat weight between 40-55 gsm for adhesion optimization.",
    "Use crosslinker level above 0.5% to control residue.",
    "Run next DOE on backing film thickness and film permeability to improve MVTR."
  ]
}
```

## 22.5 Four Layers of Learning

Separate learning into four layers:

```text
Layer 1 — Raw data
Layer 2 — Statistical finding
Layer 3 — Technical interpretation
Layer 4 — Decision recommendation
```

### Layer 1 — Raw Data

```markdown
| Sample | Coat Weight | Crosslinker | Peel | MVTR | Residue |
|---|---:|---:|---:|---:|---:|
| S1 | 25 | 0.2 | 0.8 | 920 | 2 |
| S2 | 40 | 0.5 | 1.6 | 880 | 1 |
| S3 | 55 | 0.8 | 2.4 | 850 | 0 |
```

### Layer 2 — Statistical Finding

```markdown
| X | Y | Relationship | Confidence | Notes |
|---|---|---|---|---|
| Coat weight | Peel adhesion | Positive | High | Statistically significant |
| Coat weight | MVTR | Weak / unclear | Medium | Not significant in tested range |
| Crosslinker | Residue | Negative | High | Higher crosslinker reduced residue |
```

### Layer 3 — Technical Interpretation

```text
The tested adhesive coat weight range mainly affected peel adhesion, but did not strongly influence MVTR. This suggests breathable performance may be dominated by backing film permeability or adhesive chemistry rather than coating amount within 25-55 gsm.
```

### Layer 4 — Decision Recommendation

```text
Proceed with 40-55 gsm coat weight window. Keep crosslinker ≥0.5%. For next experiment, investigate backing film thickness and film permeability as primary MVTR levers.
```

## 22.6 Hypothesis Status Categories

Each hypothesis should be classified as:

```text
Confirmed
Partially confirmed
Contradicted
Inconclusive
Not tested
Not comparable due to method deviation
```

## 22.7 Range Awareness

Every learning must include the tested range.

Bad learning:

```text
Coat weight does not affect MVTR.
```

Better learning:

```text
Within 25-55 gsm for this adhesive/backing system, coat weight did not show a statistically significant effect on MVTR.
```

## 22.8 Contradiction Handling

If results contradict patent-derived assumptions, the system should show the contradiction explicitly.

```markdown
# Contradiction Detected

Prior evidence:
Patent A suggested higher coat weight reduced MVTR.

New result:
Experiment EXP-2026-001 showed no significant MVTR reduction from 25-55 gsm.

Possible explanations:
1. Patent used different backing film.
2. Patent tested wider coat weight range.
3. Patent used different MVTR method.
4. Current adhesive is more permeable.
5. Sample size was insufficient.

Recommended action:
Run confirmatory DOE with wider coat weight range or isolate backing film effect.
```

---

# 23. Loop 21 — Knowledge Base Update

## 23.1 Objective

Convert approved learning records into reusable organizational knowledge.

## 23.2 Core Knowledge Objects

```text
Project
 ├── VOC
 ├── CTQ
 ├── Evidence Source
 │    ├── Patent
 │    ├── Internal Report
 │    ├── Product Benchmark
 │    └── Literature
 ├── Hypothesis
 ├── Experiment
 │    ├── Factor X
 │    ├── Response Y
 │    ├── Sample Matrix
 │    ├── Test Result
 │    └── Statistical Analysis
 ├── Learning Record
 └── Next Experiment Recommendation
```

## 23.3 Learning Record Schema

```text
LearningRecord
- learning_id
- project_id
- experiment_id
- source_hypothesis_id
- x_variable
- y_response
- expected_direction
- observed_direction
- effect_size
- statistical_confidence
- confirmed_status
- tested_range
- material_system
- process_condition
- test_method
- limitation
- recommendation
- reviewer_status
- reviewer_comment
- created_at
- updated_at
```

## 23.4 Knowledge Update Workflow

```text
1. AI proposes learning update
2. Scientist reviews evidence
3. Scientist approves, edits, rejects, or marks as needs more data
4. Approved learning enters project knowledge base
5. Cross-project reusable design rules are suggested
6. Design rules are reviewed by subject matter experts
```

## 23.5 Design Rules

Over time, the system should generate internal design rules.

```markdown
# Emerging Design Rules

1. For adhesive family A, coat weight between 40-55 gsm gives acceptable peel adhesion.
2. Crosslinker below 0.5% increases residue risk.
3. MVTR is more sensitive to backing film permeability than adhesive coat weight in the current construction.
4. Silicone-rich adhesive reduces removal force but may increase edge lift under moisture challenge.
```

Each design rule must be traceable to:

```text
Supporting experiments
Contradicting evidence
Valid material systems
Valid tested ranges
Valid test methods
Confidence level
Reviewer approval
```

---

# 24. Claude Code Skill Implementation

## 24.1 Skill Name

```text
rd-patent-doe-intelligence-skill
```

## 24.2 Skill Purpose

Help R&D teams translate VOC into technical specifications, mine patents and internal evidence, extract DOE/X-Y relationships, generate experiment designs, and update learning after experiments.

## 24.3 Suggested Skill Folder Structure

```text
rd-patent-doe-intelligence-skill/
│
├── SKILL.md
├── templates/
│   ├── voc_intake_template.md
│   ├── technical_spec_matrix.md
│   ├── patent_search_protocol.md
│   ├── patent_extraction_template.md
│   ├── xy_correlation_matrix.md
│   ├── experiment_design_template.md
│   ├── post_experiment_learning_template.md
│   └── final_report_template.md
│
├── rubrics/
│   ├── patent_relevance_scoring.md
│   ├── evidence_quality_scoring.md
│   ├── doe_quality_scoring.md
│   ├── transferability_scoring.md
│   └── learning_confidence_scoring.md
│
├── workflows/
│   ├── 01_voc_to_ctq.md
│   ├── 02_business_validation.md
│   ├── 03_internal_knowledge_mining.md
│   ├── 04_patent_landscape.md
│   ├── 05_patent_shortlist.md
│   ├── 06_patent_doe_extraction.md
│   ├── 07_xy_synthesis.md
│   ├── 08_experiment_recommendation.md
│   ├── 09_lab_execution_plan.md
│   └── 10_post_experiment_learning.md
│
└── examples/
    ├── example_input_voc.md
    ├── example_patent_summary.md
    ├── example_experiment_plan.md
    ├── example_learning_record.md
    └── example_final_output.md
```

## 24.4 Skill Evidence Rules

The Skill should always follow these rules:

```text
1. Separate facts, extractions, inferences, and recommendations.
2. Mark confidence level for every extracted relationship.
3. Never treat patent examples as validated commercial truth.
4. Flag missing data, ambiguous claims, unsupported conclusions, and method differences.
5. Do not provide legal freedom-to-operate conclusions.
6. Require human review before final DOE and knowledge-base update.
7. Preserve traceability to source documents, patent examples, and experiment IDs.
```

## 24.5 Mandatory Skill Output

```text
1. VOC translation brief
2. Business validation scorecard
3. CTQ matrix
4. Regulatory / claim feasibility screen
5. Internal knowledge summary
6. Commercial benchmark summary
7. Patent search protocol
8. Top company list
9. Top patent shortlist
10. Patent-by-patent DOE extraction
11. Test method comparability matrix
12. Cross-patent X-Y synthesis
13. White-space / design-around analysis
14. IP risk pre-screen
15. Manufacturing and supplier feasibility screen
16. Risk management mapping
17. Experiment portfolio prioritization
18. DOE design details
19. Lab execution plan
20. Post-experiment learning report
21. Knowledge-base update proposal
22. Next-round experiment recommendation
```

---

# 25. App Implementation

## 25.1 App Concept

Build an internal **R&D Intelligence Workbench**.

## 25.2 Recommended Architecture

```text
Frontend
Django templates / React / Streamlit
    ↓
Workflow Orchestrator
Python services / Celery / agent workflow
    ↓
Data Connectors
Patent APIs, internal documents, VOC database, lab data
    ↓
AI Extraction Layer
LLM + embedding search + structured extraction
    ↓
Knowledge Store
PostgreSQL + vector database
    ↓
Analysis Engine
Pandas / statsmodels / scipy
    ↓
Report Generator
Markdown / Word / PowerPoint / Excel
```

## 25.3 Practical Stack for Internal MVP

```text
Django + HTML/CSS/JS
PostgreSQL
Celery for background jobs
Redis for queue/cache
Pandas for data manipulation
Statsmodels or scipy for statistical analysis
ECharts for visualization
LLM API for extraction and interpretation
python-docx / python-pptx / openpyxl for export
```

## 25.4 Main App Screens

```text
1. Project Dashboard
2. VOC Intake
3. Business Validation
4. CTQ Builder
5. Internal Knowledge Search
6. Benchmark Product Workspace
7. Patent Search Setup
8. Patent Ranking Dashboard
9. Patent Extraction Workspace
10. X-Y Correlation Matrix
11. Feasibility and Risk Review
12. Experiment Generator
13. DOE Plan Review
14. Lab Execution Plan
15. Result Upload
16. Auto Analysis
17. Post-Experiment Learning
18. Knowledge Update Review
19. Next Experiment Recommendation
20. Report Export
```

## 25.5 MVP Scope

Start with a narrow but valuable MVP:

```text
Input:
- VOC statement
- optional competitor list
- uploaded patent PDFs or patent text
- optional internal reports
- DOE result Excel file

AI outputs:
1. VOC-to-CTQ matrix
2. patent-by-patent extraction
3. X-Y correlation matrix
4. 5 initial experiment designs
5. DOE result analysis
6. post-experiment learning report
7. updated X-Y knowledge matrix
8. next experiment recommendation
```

---

# 26. Traceability and Governance

## 26.1 Traceability Chain

Every recommendation should be traceable:

```text
Source document
    ↓
Extracted fact
    ↓
AI interpretation
    ↓
Human-reviewed learning
    ↓
Design rule
    ↓
Experiment recommendation
```

## 26.2 Audit Trail

The system should track:

- Source document ID
- Patent number or report ID
- Claim number or example number
- Extracted text or data location
- AI extraction timestamp
- Model version
- Reviewer name
- Reviewer decision
- Version history
- Final approved output

## 26.3 Data Security

A Fortune 500 deployment must define:

```text
1. What information can be sent to external LLMs?
2. What must stay in an internal environment?
3. How are confidential VOCs handled?
4. How are internal lab data and reports protected?
5. Who can access each project?
6. What is the data retention policy?
7. Are embeddings allowed for confidential documents?
8. How are IP-sensitive documents handled?
```

---

# 27. Final Report Template

```markdown
# R&D Patent-to-Experiment Intelligence Report

## 1. Executive Summary
- Customer need
- Technical opportunity
- Main design levers
- Main risks
- Recommended experiment strategy

## 2. VOC Translation
- Original VOC
- Clarified needs
- Ambiguities
- Technical interpretation

## 3. Business Validation
- Market relevance
- Customer segment
- Competitive pressure
- Business priority

## 4. CTQ Matrix
- Customer needs
- Technical metrics
- Test methods
- Initial targets

## 5. Regulatory and Claim Feasibility
- Intended claims
- Evidence required
- Claim risk

## 6. Internal Knowledge Summary
- Prior work
- Known failures
- Reusable platforms

## 7. Commercial Benchmark Summary
- Competitor products
- Claims
- Likely mechanisms
- Gaps

## 8. Patent Landscape Summary
- Search strategy
- Top companies
- Technology clusters
- Top patents

## 9. Patent Technical Extraction
For each patent:
- Purpose
- Product structure
- Material system
- Key claims
- Experimental examples
- Input Xs
- Output Ys
- X-Y relationships
- Limitations

## 10. Test Method Comparability
- Method differences
- Unit differences
- Comparability concerns

## 11. Cross-Evidence X-Y Synthesis
- Recurring variables
- Recurring output metrics
- Tradeoff map
- Confidence levels

## 12. White-Space and Design-Around Analysis
- Crowded areas
- Potential white space
- Design-around options

## 13. Feasibility and Risk Screen
- IP risk signals
- Manufacturing feasibility
- Supplier feasibility
- Risk management mapping

## 14. Recommended Experiments
- Experiment portfolio
- DOE details
- Controls
- Decision criteria

## 15. Lab Execution Plan
- Sample matrix
- Sample IDs
- Test requests
- Data capture template

## 16. Post-Experiment Learning
- Results summary
- Statistical findings
- Hypothesis evaluation
- Updated X-Y matrix
- Contradictions
- Technical interpretation

## 17. Knowledge Base Update
- Approved learning records
- Emerging design rules
- Confidence levels

## 18. Next Experiment Recommendation
- Next DOE options
- Rationale
- Decision gates

## 19. Open Questions
- Missing data
- Business assumptions
- IP/legal questions
- Test method gaps
- Manufacturing concerns

## 20. Appendix
- Patent scoring matrix
- Extraction tables
- Raw data references
- Statistical analysis details
```

---

# 28. Implementation Roadmap

## Stage 1 — Workflow Skill

Build a Claude Code Skill first to standardize thinking.

Focus:

```text
VOC translation
CTQ matrix
Patent extraction
X-Y synthesis
Experiment design
Post-experiment learning report
```

Benefits:

- Fast to prototype
- Low engineering overhead
- Good for developing templates and rubrics
- Helps align scientist expectations

## Stage 2 — Internal MVP App

Build a Django-based internal workbench.

Focus:

```text
Project management
Document upload
AI extraction
Human review
X-Y matrix
DOE generator
Result upload
Learning report
Export
```

Benefits:

- Reusable by multiple teams
- Better governance
- Structured database
- Easier review and approval

## Stage 3 — Integrated R&D Intelligence Platform

Integrate enterprise data systems.

Focus:

```text
Patent databases
Internal document repositories
ELN / LIMS
Regulatory claim database
Supplier database
Material library
Historical DOE database
```

Benefits:

- Closed-loop learning
- Cross-project design rules
- Portfolio-level intelligence
- Faster R&D decision-making

---

# 29. One-Sentence Summary

> The AI-enabled R&D loop should convert VOC into CTQs, mine internal and external evidence, extract X-Y relationships, design experiments, capture results, update technical knowledge, and recommend the next best experiment under human review.

---

# 30. Minimum Viable Version

If the full loop feels too complex, start with this:

```text
1. Capture VOC
2. Translate VOC to CTQs
3. Upload 10-15 selected patents
4. Extract Xs, Ys, and DOE details
5. Generate X-Y matrix
6. Propose 5 experiments
7. Upload experiment results
8. Generate learning report
9. Update approved X-Y matrix
10. Recommend next experiment
```

This is enough to prove value without building the full enterprise platform immediately.

---

# 31. Key Principle to Remember

A normal R&D archive stores documents.

An AI-enabled R&D learning system stores:

```text
Hypotheses
Evidence
Experiments
Results
Learnings
Design rules
Next actions
```

That is the difference between a document repository and a real R&D intelligence engine.
