# Example Patent Extraction Mini-Demo

## Patent Context
A patent discloses a breathable adhesive dressing with examples varying adhesive coat weight and backing film thickness.

## Extracted Xs
| X | Category | Range | Tested? |
|---|---|---:|---|
| Adhesive coat weight | Structure/process | 25-55 gsm | Yes |
| Backing film thickness | Structure | 15-35 µm | Yes |
| Crosslinker level | Composition | 0.2-0.8% | Yes |

## Extracted Ys
| Y | Unit | Method | Direction |
|---|---|---|---|
| Peel adhesion | N/25 mm | 180° peel on steel | within_range |
| MVTR | g/m²/24h | cup method | higher_better |
| Residue | score | visual rating | lower_better |

## Relationship Statement
Within Examples 1-5, adhesive coat weight from 25-55 gsm is associated with increased peel adhesion. MVTR relationship is unclear because backing film thickness also changes. Evidence level 3 due to confounding. Confidence medium.
