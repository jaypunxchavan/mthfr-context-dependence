"""Data integrity / reproducibility checks."""
import pandas as pd
from scipy import stats as scipy_stats

AA3TO1 = {
    'Ala':'A','Arg':'R','Asn':'N','Asp':'D','Cys':'C','Gln':'Q','Glu':'E',
    'Gly':'G','His':'H','Ile':'I','Leu':'L','Lys':'K','Met':'M','Phe':'F',
    'Pro':'P','Ser':'S','Thr':'T','Trp':'W','Tyr':'Y','Val':'V'
}

def parse_hgvs(hgvs):
    """e.g. 'p.Ala350Ile' -> (350, 'A', 'I'). Returns None for synonymous ('=')
    or unparseable entries (e.g. stop-gain 'Ter', which insilico.csv doesn't
    score anyway -- these fail the match step regardless)."""
    s = str(hgvs).strip('"').replace('p.', '')
    ref3, rest = s[:3], s[3:]
    i = 0
    while i < len(rest) and rest[i].isdigit():
        i += 1
    pos = int(rest[:i])
    alt3 = rest[i:]
    if alt3 == '=' or alt3 not in AA3TO1:
        return None
    return pos, AA3TO1.get(ref3), AA3TO1.get(alt3)

def reproducibility_check(llr_df, insilico_df):
    """Merge atlas pathogenicity LLR against PolyPhen-2/SIFT/PROVEAN; report
    Spearman correlation direction as a pipeline sanity check.

    Confirmed passing (n=8701 after dropping missing llr and match failures):
      provean ~ -0.38   sift ~ -0.32   pp2div ~ +0.30   pp2var ~ +0.32

    Note: ~479/10136 llr values are NaN (largely stop-gain variants the
    atlas's own model didn't score) -- these are dropped explicitly here,
    not silently. If your numbers come back far off the values above, the
    merge/parsing is wrong before ESM-2 has been touched at all.
    """
    parsed = llr_df["hgvs"].apply(parse_hgvs)
    keep = parsed.notna()
    merged = pd.DataFrame({
        "pos":  [p[0] if p else None for p in parsed[keep]],
        "ref":  [p[1] if p else None for p in parsed[keep]],
        "alt":  [p[2] if p else None for p in parsed[keep]],
        "llr":  llr_df.loc[keep, "llr"].values,
    })
    merged = merged.merge(insilico_df, on=["pos", "ref", "alt"], how="inner")

    cols = ["llr", "provean", "sift", "pp2div", "pp2var"]
    before = len(merged)
    merged = merged.dropna(subset=cols)
    dropped = before - len(merged)
    if dropped:
        print(f"Dropped {dropped} rows with missing values in {cols} (kept {len(merged)})")

    results = {}
    for pred in ["provean", "sift", "pp2div", "pp2var"]:
        rho, p = scipy_stats.spearmanr(merged["llr"], merged[pred])
        results[pred] = {"rho": rho, "p": p, "n": len(merged)}
    return results
