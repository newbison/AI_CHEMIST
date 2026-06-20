# Patent Priority List

> Output of workflow 04a_patent_search_and_rank. This is the ranked set handed to patent-xy-extraction-skill.

## Parameters
- Top-N applied: [value]
- Relevance cutoff: score >= 30
- Total candidates scored: [value]
- Candidates >= 30: [value]
- Selected for extraction: [value]

## Selected for Extraction (top-N, score >= 30, Verified = Y)
> Every row MUST be backed by a fetched source. Patent/Publication must include the kind code (A/B/U). Source URL empty → reject the row. See `workflows/04a_patent_search_and_rank.md` Retrieval & Anti-Fabrication Rules.

| Rank | Patent / Publication (with kind code) | Assignee | Title (short) | Score | Why Included | Extraction Priority | Source URL | Retrieved | Verified |
|---:|---|---|---|---:|---|---|---|---|:---:|

## Background Only (score < 30, or Verified = N)
| Patent / Publication | Assignee | Score | Verified | Reason Not Extracted |
|---|---|---:|:---:|---|

## Provenance & Verification Notes
- Retrieval channel(s) used (webapp backend / web search / user-supplied): 
- Any patent whose number was real but assignee/subject did not match the fetched source (dropped or corrected): 
- Any search block that returned 0 retrievable results: 
- If retrieval was unavailable, state it here and confirm the list was halted (no unverified patents emitted): 

## Notes
- 
