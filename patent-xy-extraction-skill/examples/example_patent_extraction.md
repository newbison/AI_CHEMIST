# Example Patent Extraction Mini-Demo

## Patent Context
A patent discloses a UV-curable hard coat for polycarbonate with examples varying oligomer molecular weight and silicone content.

## Extracted Xs
| X | Category | Range | Tested? |
|---|---|---:|---|
| Oligomer molecular weight | Composition | 500-2000 Da | Yes |
| Silicone content | Composition | 5-20% | Yes |
| UV dose | Process | 500-2000 mJ/cm² | Yes |

## Extracted Ys
| Y | Unit | Method | Direction |
|---|---|---|---|
| Pencil hardness | H scale | ASTM D3363 | higher_better |
| QUV ΔE | — | ASTM G154 5000h | lower_better |
| Crosslink density | mol/cm³ | DMA | higher_better |

## Relationship Statement
Within Examples 1-5, silicone content from 5-20% is associated with improved weatherability but reduced hardness. The tradeoff is modulated by UV dose. Evidence level 4 due to controlled experiments. Confidence high.
