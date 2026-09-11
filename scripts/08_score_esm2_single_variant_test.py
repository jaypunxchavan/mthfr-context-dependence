"""
Step 8: Single-variant ESM-2 test.

Score exactly one variant (p.Ala222Val) end to end with masked-marginal
scoring before scaling to ~12,000. Requires: pip install torch fair-esm
(not in the base requirements.txt -- large download, add when ready).

Cache results to data/processed/ -- this should not live in notebook cell
state.
"""
