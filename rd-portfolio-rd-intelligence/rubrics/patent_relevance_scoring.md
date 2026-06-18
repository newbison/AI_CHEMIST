# Patent Relevance Scoring Rubric

Score each patent from 0 to 5 on each dimension.

## Dimensions

1. VOC semantic match
2. CTQ metric match
3. Material-system match
4. Product-construction match
5. Experimental data richness
6. DOE usefulness
7. Test-method disclosure
8. Transferability to current platform
9. Claim overlap / IP risk signal
10. White-space insight value

## Suggested Interpretation

```text
40-50: high priority for deep extraction
30-39: relevant, extract selectively
20-29: background evidence
<20: low relevance unless strategically important
```

## Output

```markdown
| Patent | Score | Why Included | Main Limitation | Extraction Priority |
|---|---:|---|---|---|
```
