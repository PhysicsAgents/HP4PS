# Taxonomy sources

English | [中文](README.zh.md)

The first three levels of the HP4PS taxonomy (domain, subfield, branch) are PACS 2010, with GB/T 13745-2009 discipline codes attached to the matching nodes. `python scripts/build_taxonomy.py` turns the tables here into `homepage/data/taxonomy.json`; edit the tables, never the JSON.

## Tables

| File | Content | Source |
|---|---|---|
| `pacs2010_levels1-3.tsv` | PACS 2010 codes, levels 1–3, with English names: 10 domains, 67 subfields, 716 branches | AIP PACS 2010 regular edition, as scraped in [canderson/PACS](https://github.com/canderson/PACS) (`pacs.yml`, `source: main`) |
| `pacs2010_zh.tsv` | Chinese name of every PACS code above | Translated for HP4PS; physics terms follow common Chinese usage and the GB/T 13745 names where they match |
| `gb13745_2009_physics.tsv` | All GB/T 13745-2009 codes under 140 Physics | Text of GB/T 13745-2009 |
| `gb_to_pacs.tsv` | Which PACS nodes each GB/T code is attached to | Mapping made for HP4PS |

## Rules

- PACS sets the tree. GB/T 13745 adds codes to nodes and never adds nodes.
- Every 140 Physics code is attached to at least one PACS node; the build fails otherwise. A GB/T code may sit on several nodes, and a node may carry several GB/T codes; neither means the two are equivalent.
- Where PACS covers ground that GB/T 13745 files outside physics, codes from 130 Mechanics, 160 Astronomy and 170 Earth Science are attached instead. Their "other" and history codes, and branches with no physics counterpart, are left out.
- A GB/T "other" code (xx99) goes on the PACS "Other topics" node of the same section, or on its parent's nodes when there is none.
- Left out of PACS: level-4 and level-5 codes, acoustics-appendix codes, and 99.10 Errata.
- Levels 4 and 5 (research path, technical path) are not fixed in advance; each entry states its own.
