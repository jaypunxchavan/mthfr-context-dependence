"""
Script 41: documents the confirmation-run leakage fix in RESULTS.md.

An independent audit (a separate chat working on this same repo) found
that scripts/28_confirmation_run.py's B3c sign-flip null stage fit the
interaction model's bias-correction smoother on the FULL raw dataset
(explore+confirm combined) before subsetting to confirm-half rows --
confirm-half data leaking into what the docstring claimed was an
explore-only fit. B2/B3a (baseline correlation) and B3b (multivariable
controls) were independently verified clean; the leak was isolated to
B3c specifically.

Fixed by separating what's genuinely per-variant (each variant's own
WT-arm fit -- cannot leak, since it never pools across variants) from
what's genuinely pooled across variants (the bias-correction smoother,
now correctly restricted to explore-half rows only). Rerun at full
resolution (N_PERM=3000): p=0.0017 (rank), p<0.0003 (calibrated),
essentially unchanged from the leaked version. The confirmation run's
conclusion survives being done correctly.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    cr = pd.read_csv(PROC / "confirmation_run_results.csv")
    sf = cr[cr.stage == "signflip_null"]

    L = ["## Confirmation run — leakage found and fixed\n"]
    L.append("**A data-leakage bug was found in the confirmation run's sign-flip null "
             "stage (B3c) by an independent audit of this repository, verified directly "
             "against the code, and fixed.** The bias-correction smoother inside the "
             "interaction-model reimplementation was fit on the full raw dataset "
             "(explore+confirm combined) before subsetting to confirm-half rows -- "
             "confirm-half information leaking into what the code claimed was an "
             "explore-only fit. The other two stages (baseline correlation, "
             "multivariable controls) were checked directly and confirmed clean.\n")
    L.append("**After the fix** (bias-correction smoother restricted to explore-half rows "
             "only; each variant's own per-row WT-arm fit, which cannot leak across the "
             "split, computed as before), rerun at N_PERM=3000:\n")
    if len(sf):
        L.append("| Error metric | p-value (post-fix) |")
        L.append("|---|---|")
        for _, r in sf.iterrows():
            L.append(f"| {r.error_metric} | {r.p if r.p>0 else '<0.0003'} |")
        L.append("")
    L.append("**The result survives essentially unchanged.** The leak was real and worth "
             "fixing on principle, but it was not manufacturing the confirmation run's "
             "conclusion.\n")

    text = "\n".join(L)
    results_path = ROOT / "RESULTS.md"
    existing = results_path.read_text() if results_path.exists() else ""
    marker = "## Confirmation run"
    if marker in existing:
        idx = existing.index(marker)
        pre, rest = existing[:idx], existing[idx:]
        nxt = rest.find("\n## ", 1)
        existing = pre + text + (rest[nxt:] if nxt != -1 else "")
    else:
        existing = existing + "\n" + text
    results_path.write_text(existing)
    print(f"RESULTS.md updated with leakage-fix note ({len(text)} chars)")
