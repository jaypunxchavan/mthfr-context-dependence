# Does Protein Language Model Error Concentrate in Context-Dependent Variants?

MTHFR context-dependence project. See `config/audit_log.md` for the running
log of every data decision made along the way.

## Setup
    source venv/bin/activate
    pip install -r requirements.txt

In VSCode, select the "Python (mthfr-context)" kernel for notebooks (or
point at venv/bin/python directly if kernel registration didn't run).

## Structure

- `scripts/lib/` — the actual reusable logic (data loading, sequence
  verification, validation checks, stats). Import from here.
- `scripts/0X_*.py` — numbered, run-in-order entry points. Thin wrappers
  around `lib/`. Use these for anything expensive, cached, or load-bearing:
  data audits, ESM-2 scoring (caches to disk — should not live in notebook
  cell state), pre-registered statistical tests.
- `notebooks/` — exploration, plotting, one-off checks. Imports from
  `scripts/lib/` rather than reimplementing anything. Not the place for
  logic that the final result depends on.

## Data
`data/raw/` holds an untouched copy of jweile/mthfrModel (gitignored — large,
and it's reference material, not your work). `data/processed/` holds your
own merged/cleaned tables.

## Pipeline order
Run scripts/0X_*.py in numeric order. See config/audit_log.md for what's
been verified so far.
