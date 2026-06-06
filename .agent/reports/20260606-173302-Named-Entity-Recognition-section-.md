## Task: Named Entity Recognition section
Date: 2026-06-06T17:33:02Z
Branch: agent/named-entity-recognition-section-20260606-1729

DECIDED: Grouped entities by label/type rather than a flat list, and sorted labels alphabetically in output. This makes the NER section scannable and consistent across runs. Used `Counter.most_common(20)` per label to match the existing bigram limit convention.
NOTICED: The existing `analyze_stanza()` called `stanza.Pipeline("sr", use_gpu=False)` with no explicit `processors` — the previous code relied on Stanza's default processor set which may or may not include NER depending on the version/model; making it explicit is strictly safer.
UNCERTAIN: Stanza's Serbian model (`sr`) may not have an NER component in all versions — if it doesn't, the `ner` processor in the pipeline string will raise at runtime. The task says "using the existing models", so I kept the `sr` language but added the processor string; a runtime graceful fallback wasn't requested.
WISHED_FOR: Knowing which spaCy and Stanza model versions are actually deployed would have let me verify the NER label sets (e.g., GPE vs LOC) and confirm the Stanza `sr` model ships an NER component.
