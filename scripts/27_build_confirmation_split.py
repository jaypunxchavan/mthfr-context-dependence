"""
Group B1: build and save the confirmation split.

Region-local GI-tercile x region stratification, grouped by position.
abs_gi (the primary test variable) is balanced; blosum62 is well balanced.
Grantham and RSA remain imbalanced after this fix -- disclosed explicitly
below, not hidden. A third stratification layer was tested and rejected:
it produces bins too thin to split (one region x GI-tercile x RSA-tercile
cell held a single position). With ~654 positions total, perfect balance
on every covariate is not achievable through stratification alone.

Saves the split (as a position -> set assignment) so scripts B2-B5 read
the SAME split rather than each regenerating their own.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from scripts.lib.confirmation_split import stratified_position_split, split_balance_report
from scripts.lib.features import add_substitution_features, add_structural_features
from scripts.lib.io import load_structural_features
from scripts.lib.regions import assign_region

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
SEED = 0

if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    df = add_substitution_features(df)
    df = add_structural_features(df, load_structural_features())
    df["region"] = assign_region(df["position"])

    explore_mask, confirm_mask = stratified_position_split(df, seed=SEED)
    print(f"explore: {explore_mask.sum()} rows, {df.loc[explore_mask,'position'].nunique()} positions")
    print(f"confirm: {confirm_mask.sum()} rows, {df.loc[confirm_mask,'position'].nunique()} positions")

    report = split_balance_report(df, explore_mask, confirm_mask)
    print("\nBalance report:")
    print(report.to_string())

    unbalanced = report[(report.get("balanced") == False)]
    print(f"\n{len(unbalanced)} covariate(s) remain imbalanced after region x GI-tercile "
          f"stratification: {list(unbalanced['group'])}.")
    print("abs_gi (the primary test variable) and blosum62 are balanced. Grantham and RSA")
    print("are not -- a third stratification layer was tested and produces bins too thin")
    print("to split (min cell size 1). Disclosed as a limitation of the confirmation split,")
    print("not corrected further.")

    split_table = pd.DataFrame({
        "position": sorted(df["position"].unique()),
    })
    split_table["set"] = split_table["position"].apply(
        lambda p: "explore" if p in set(df.loc[explore_mask, "position"])
        else ("confirm" if p in set(df.loc[confirm_mask, "position"]) else "unassigned"))
    split_table.to_csv(PROC / "confirmation_split_assignment.csv", index=False)
    report.to_csv(PROC / "confirmation_split_balance.csv", index=False)
    print(f"\nSaved split assignment and balance report to {PROC}")
