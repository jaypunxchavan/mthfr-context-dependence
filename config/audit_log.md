# Audit Log

Every filtering decision, exclusion, and data-integrity finding, dated.
Append — don't rewrite history here.

## Template
### YYYY-MM-DD — <what was checked>
- Finding:
- Action taken:
- Affects: (which script / which downstream step)

---

### 2026-09-14 — Tier 2 and Task 1 complete

- Sign-flip re-derivation null, central_error_rank: observed rho=+0.1199, null mean=+0.0977, excess=+0.0222 (81% artifact), p=0.0003, n_perm=10000.
- Sign-flip re-derivation null, central_error_cal: observed rho=-0.1297, null mean=-0.1015, excess=-0.0282 (78% artifact), p=<0.0001, n_perm=10000.
- Rejected design recorded: cross-variant pairing for the e_b null was miscalibrated (imports unrelated baseline severity that the multiplicative expectation exists to remove) and would reject the null regardless of ground truth. Replaced with within-variant sign flips.
- Sanity checks: all-+1 flips reproduce real e_b exactly (0.0e+00); all--1 flips give exactly -e_b.
- Grantham distance implementation was wrong on first write (constants placed inside the sqrt rather than multiplying squared differences); corrected and verified against ten published table values, max dev 0.87.
- The logl gap between own and published single-arm fits is a CONSTANT 12.5534 (sd 4.7e-06) that cancels in the LOD — not optimizer convergence, as initially misread.
- Environment-dependent context does not survive multivariable controls.
- RESULTS.md is now auto-generated from the result CSVs by script 22.

### 2026-09-16 — Robustness follow-ups

- Confirmation run (script 28) executed on the held-out confirm half, pipeline frozen from the explore half, including multivariable controls (added specifically because finding #4 was called strongest partly for surviving those controls -- a frozen pipeline that skipped them would have validated a weaker claim than the one being tested). See confirmation_run_results.csv for full numbers.
- CORRECTION: z-scores throughout this project (mechanical baseline, region-2, findings #3/#4) were reported as if equally precise to the permutation p-value ceiling. They are not -- the p-value (bounded by 1/n_draws) is the empirically demonstrated claim; the z-score assumes the null's tail is Gaussian, unverified with a few hundred draws that far out. Both are now reported with this distinction stated explicitly.
- Finding #4's z-scores shifted (4.74/10.54 at n_perm=300 -> 5.01/10.78 at n_perm=500) as the null mean/sd estimate refined with more draws -- expected refinement between rounds, not two conflicting findings, noted explicitly so it doesn't read as unreconciled in the record.
- Confirmation split (script 27) stratifies on abs_gi's MARGINAL distribution across both halves -- this does not touch the error~GI relationship under test (that requires looking at error, which balancing never does) and protects against range restriction mechanically shrinking an observed correlation regardless of whether the true relationship holds. Not circular; stated explicitly given it can look that way at a glance.

### 2026-09-16 — Audit log deduplication

- Finding: the "Tier 2 and Task 1 complete" entry had been appended six times (2026-09-14 x1, 2026-09-16 x5) with growing but overlapping content, because script 22's audit-append logic rebuilt the full entry from scratch on every run with no check for whether that content already existed in the file.
- Action taken: manually deduplicated to the two entries above, and fixed script 22 (see scripts/lib/audit.py) to check line-by-line for existing content before appending, so only genuinely new facts get written from here forward.
- Affects: config/audit_log.md going forward; the two entries above are the complete, correct history of everything logged through this point.

### 2026-09-16 — Robustness follow-ups

- Sign-flip re-derivation null, central_error_rank: observed rho=+0.1199, null mean=+0.0980, excess=+0.0219 (82% artifact), p=<0.0001, n_perm=150.
- Sign-flip re-derivation null, central_error_cal: observed rho=-0.1297, null mean=-0.0996, excess=-0.0301 (77% artifact), p=<0.0001, n_perm=150.
