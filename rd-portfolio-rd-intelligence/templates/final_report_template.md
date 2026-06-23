# [根据 VOC 和专利内容，自动生成一个简洁、专业的报告标题，格式如：「XXX 技术专利分析报告」或「XXX 技术/材料研究报告」或「XXX 领域专利全景与技术洞察」- 标题长度控制在20字以内，英文不超过25个单词，直接以 # 标题 开头，不要用引号]

## 1. Executive Summary
- Customer need:
- Technical opportunity:
- Main design levers:
- Main risks:
- Recommended experiment strategy:
- Recommended next decision:

## 2. Project and Portfolio Intake
- Project:
- Portfolio:
- Product category:
- Platform:
- Material system:
- Target region:
- Replication scope:

## 3. VOC Translation
- Original VOC:
- Interpreted needs:
- Ambiguities:
- Clarifying questions:

## 4. CTQ Matrix
| Customer Need | CTQ | Y Metric | Test Method | Initial Target | Risk |
|---|---|---|---|---|---|

## 5. Market Insights / 市场洞察
> 本章节整合了 Deep Search 管线自动生成的市场份额排名、重点公司优先级、技术路线格局和 FTO 筛查结果。

- **市场份额与竞争格局**：
- **重点公司技术布局**：
- **技术路线分布**：
- **FTO 风险评估**：
- Internal knowledge:
- Commercial benchmarks:
- Literature / standards:

## 6. Patent Technical Extraction Summary
| Patent | Assignee | Key Xs | Key Ys | Useful DOE Evidence | Limitations |
|---|---|---|---|---|---|

## 7. Test Method Comparability
| Metric | Source Method | Internal Method | Comparable? | Concern |
|---|---|---|---|---|

## 8. Cross-Evidence X-Y Synthesis
| X | Y | Direction | Evidence | Confidence | Valid Context |
|---|---|---|---|---|---|

## 9. White-Space and Design-Around Opportunities
- Crowded areas:
- Potential white space:
- Design-around paths for IP counsel review:

## 10. Feasibility and Risk Screen
- IP risk signals:
- Regulatory / claim feasibility:
- Manufacturing feasibility:
- Supplier feasibility:
- Design risk mapping:

## 11. Experiment Portfolio — 1st Round: Factor Screening
> **Goal**: From all critical X variables extracted from patents, identify the 2-4 dominant levers that actually drive CTQs. Use fractional factorial design (e.g. 2^(k-p), Resolution≥IV). Narrow 5-10 candidate Xs → 2-4 dominant levers.

| Rank | Experiment | Learning Goal | Key Xs Tested | Priority Rationale | Required Gate |
|---:|---|---|---|---|---|

### Screening DOE Design
- **Design type**: [e.g. 2^(5-1) fractional factorial, Resolution IV]
- **Factors & Levels**:
  | Factor (X) | Low (-1) | Center (0) | High (+1) | Rationale (patent source) |
  |---|---|---|---|---|
- **Responses (Y)**:
  | Response | Unit | Test Method | Target |
  |---|---|---|---|
- **Controls**: [baseline formulation / commercial benchmark]
- **Replicates**: [N per condition]
- **Decision Rule**: [Which factors proceed to Round 2? E.g. p<0.10 main effect]

---

## 12. DOE Details — 2nd Round: Response Surface Optimization
> **Goal**: For the 2-4 dominant Xs from Round 1, find the optimal parameter combination using Central Composite Design (CCD) or Box-Behnken. Try DIFFERENT X combinations than Round 1.

| Rank | Experiment | Learning Goal | Factors (from R1) | Priority Rationale | Required Gate |
|---:|---|---|---|---|---|

### Optimization DOE Design
- **Design type**: [e.g. Central Composite Design (CCD) with α=1.414 / Box-Behnken]
- **Factors & Levels**:
  | Factor (X) | Low (-α) | Low (-1) | Center (0) | High (+1) | High (+α) | Rationale |
  |---|---|---|---|---|---|---|
- **Responses (Y)**:
  | Response | Unit | Test Method | Target / Desirability |
  |---|---|---|---|
- **Controls**: [optimized baseline from R1]
- **Replicates**: [N center points, N axial points]
- **Decision Rule**: [Desirability score threshold / confirmation run criteria]

---

## 13. DOE Details — 3rd Round: Confirmation Run
> **Goal**: Run 3-5 replicates at the predicted optimal point to verify model predictions, assess long-term stability, and confirm reproducibility before scaling.

- **Optimal formulation from Round 2**:
- **Number of confirmation replicates**: [3-5]
- **Pass criteria**: [e.g. all CTQs within 95% prediction interval, CV<5% across replicates]
- **Long-term stability test**: [accelerated aging conditions, if applicable]
- **Scale-up feasibility note**:

---

## 14. Lab Execution Plan
- Sample matrix:
- Sample IDs:
- Test requests:
- Data capture template:
- Deviation log:

## 15. Post-Experiment Learning Plan
- Hypothesis record:
- Result upload expectations:
- Analysis method:
- Learning record format:
- Approval workflow:

## 16. Knowledge-Base Update Proposal
| Proposed Learning | Evidence | Confidence | Applicability | Reviewer |
|---|---|---|---|---|

## 17. Portfolio Replication Guidance
- What can be reused directly:
- What must be customized:
- What must be validated:
- Portfolio owners:

## 18. Open Questions
- Business:
- Technical:
- IP/legal:
- Regulatory:
- Manufacturing:
- Supplier:
- Test method:

## 19. Review Gates
| Gate | Owner | Status | Notes |
|---|---|---|---|
