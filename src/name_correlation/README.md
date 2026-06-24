# name_correlation

Correlates element names between the two Adams-motivic-E2 data files from
Isaksen-Wang-Xu's "Classical and C-motivic Adams charts" dataset
(DOI [10.5281/zenodo.6987157](https://doi.org/10.5281/zenodo.6987157)):

- **Adams-motivic-E2.csv** — one row per chart element, human-readable names
  (e.g. `h0 d0`, `D2`). This is what `find_differential.py` reads.
- **Adams-motivic-E2-machine.csv** — one row per F2[tau]-module generator,
  machine-assigned names of the form `{a-b}`. Carries h0/h1/h2/**h3**
  extension data the chart file doesn't.

These two files describe the same underlying data but don't share a name
space, and the chart file collapses some periodic towers (`loc`) that the
machine file enumerates individually. This script produces a best-effort
name<->name correspondence so the two can be cross-referenced — e.g. to pull
h3 extension info, or machine-generator-level detail, for an element you only
know by its chart name.

## Setup

Neither input CSV ships in this directory (the chart file is checked in
already at `src/Adams-motivic-E2.csv`; the machine file is not, to avoid
bloating the repo with another ~500KB data file). Either:

- run `./run_pipeline.sh`, which downloads `Adams-motivic-E2-machine.csv`
  from Zenodo (verified by checksum) if it's not already in `src/`, then runs
  both scripts below, or
- download it yourself from the Zenodo record above and place it next to
  `Adams-motivic-E2.csv`, or pass `--machine` pointing wherever you put it.

## Scripts

### run_pipeline.sh

Coordinator script: downloads the two input CSVs if needed (see Setup
above), then runs `correlate_motivic_names.py` followed by
`classify_h1_periodicity.py`.

```
./run_pipeline.sh [outdir]   # outdir defaults to ./out
```

### correlate_motivic_names.py

```
python3 correlate_motivic_names.py
python3 correlate_motivic_names.py --e2 PATH --machine PATH --outdir out/
```

Run with no arguments, it looks for both CSVs in `src/` (one level up from
this script) and writes output into the current directory.

### classify_h1_periodicity.py

```
python3 classify_h1_periodicity.py
python3 classify_h1_periodicity.py --e2 PATH --machine PATH --outdir out/
```

For every generator in `Adams-motivic-E2-machine.csv`, determines whether
it's h1-periodic, h1-torsion, or unknown, using the chart file's `h1target`
column (`h1target == "loc"` means h1-periodic) by way of the correlation
above. Even when `correlate_motivic_names.py` can't pin down exactly which
chart candidate a machine generator corresponds to, if *every* chart
candidate in that bidegree group has the same h1-periodicity status, the
machine generator's status is still determined — it just doesn't matter
which one of them it actually is. Writes
`Adams-motivic-h1-periodicity.csv` with columns `machine_name`, `stem`,
`Adams filtration`, `weight`, `tautorsion`, `h1_status`
(`h1-periodic`/`h1-torsion`/`unknown`), `basis` (how it was determined —
`matched (key)`, `matched (structural)`, `ambiguous-unanimous`,
`ambiguous-mixed`, or `no-chart-candidate`), and `motivic_names` (the
chart name(s) the determination is based on).

On the full computed range: 553 h1-periodic, 2919 h1-torsion, 7592 unknown
(7579 `no-chart-candidate` — periodic-tower continuations the chart has no
entry for at all; 7 genuine `ambiguous-mixed` ties; 6 `basis-mismatch
-suspected`, see below).

## How matching works

0. **Basis-mismatch check, first**: before any matching, for every `(stem,
   Adams filtration, weight)` slice where chart and machine agree on total
   dimension, compare the *multiset* of `tautorsion` values on each side.
   These should always agree — by the structure theorem for f.g. modules
   over a PID, the multiset of elementary divisors is an invariant of the
   module, regardless of which generating set either file happened to pick.
   When they don't agree (found twice in the full range, e.g. one slice
   where the chart reports three τ-periodic (τ=0) elements but the machine
   reports two τ=0 and one τ=1), the two files have a genuine difference in
   chosen basis there, and no per-element identification in that slice can
   be trusted. Those rows are pulled out into their own report (see Output)
   before anything else runs.

1. **Key match**: group the remaining rows by `(stem, Adams filtration,
   weight, tautorsion)`. A key with exactly one row on each side is a direct
   match — there's only one basis vector in that 1-dimensional piece, so
   there's nothing for a change of basis to mix it with.

2. **Structural match, single hop only**: for keys with multiple candidates
   on either side, use the h0/h1/h2 extension structure to disambiguate. A
   candidate pairing is accepted only if it's the *unique* zero-contradiction
   pairing in its group, checking agreement on which h0/h1/h2 extensions
   exist at all, both forward (this element's own extension targets) and
   backward (what other already-matched elements extend into it) — but
   "already-matched" here means **only** a Pass-1 key match, never another
   structural match. This is deliberate: chaining through other structural
   matches did resolve a few more groups in an earlier version of this
   script (occasionally 3-4 hops deep), but a multi-hop chain isn't
   independently auditable — a wrong link partway through silently
   propagates. Restricting to one hop from an unambiguous key match means
   every structural match is directly checkable against ground truth.
   (An even looser rule — not penalizing the chart for leaving an extension
   the machine has unannotated, since that's extremely common, see
   `consistency_warning` below — resolved still more groups, but isn't used
   for matching either, for the same reason: certainty over coverage.)

## Output

Four CSVs, written to `--outdir` (default: current directory):

- **Adams-motivic-name-correlation.csv** — resolved `motivic_name <->
  machine_name` pairs. `match_method` is `key` or `structural` (see above).
  `consistency_warning` is `True` if the chart claims a plain-name h0/h1/h2
  extension that the matched machine row doesn't have at all — the rare
  direction (~30 cases per extension type); the common direction (chart
  blank, machine has it — chart leaves most machine-confirmed extensions
  unannotated, by a roughly 9:1 margin in the data) is not a warning, it's
  normal. `machine_h3info`/`machine_h3target` pass through the machine
  file's h3 data, which the chart has no equivalent column for at all (see
  `find_differential.py`'s data source — the chart format simply doesn't
  carry h3 — so it can't be cross-checked, only carried along).
- **Adams-motivic-name-correlation-ambiguous.csv** — rows belonging to a key
  where multiple candidates remain on at least one side even after
  structural matching, i.e. we genuinely can't tell which is which.
- **Adams-motivic-name-correlation-unmatched.csv** — rows with *no*
  candidate at all on the other side. Mostly machine-file rows from
  `h0`/`h1`-periodic towers that the chart file collapses into a single `loc`
  entry; this is expected and not a sign of a problem.
- **Adams-motivic-name-correlation-basis-mismatch.csv** — rows from a
  `(stem, filtration, weight)` slice flagged by the Pass-0 check above.

Every row in all four files has a `name_occurrence` column. Chart names
occasionally collide — the same expression is reused for two genuinely
different elements, distinguished in the source data only by appending
`" again"` to the second one's name (e.g. `D2` / `D2 again`). These are kept
as separate, real rows rather than deduplicated; `name_occurrence` records,
in file order, which occurrence (1, 2, ...) of its base name a row is, so the
collision is explicit instead of silent.

## Known limitations (as of this writing, full computed range)

- 177 keys (684 rows) remain ambiguous even after structural matching —
  mostly cases where the candidate counts don't match between the two files
  (e.g. one chart name vs. several machine generators), so no bijection
  exists to even attempt.
- A handful of the remaining ambiguous groups mix an h1-periodic candidate
  with a non-periodic one at the same bidegree; these look like edge-of
  -computed-range effects (the machine computation may not extend far enough
  to confirm the periodic continuation the chart already asserts via `loc`)
  rather than a labeling bug worth chasing further.
- 2 slices (12 rows) are basis-mismatch-suspected, per the Pass-0 check.
- h3 cannot be used to *resolve* anything here, only exposed — the chart
  format has no h3 column at all (see module docstrings). The
  `MinimalResolution` repo's `yoneda.cpp` is the actual tool that computes
  `h_n * generator` products (for any `n`, including h3) in this same
  `{s-a}` / tau-Bockstein naming — it's almost certainly what generated the
  machine file's h0-h3 columns in the first place, and that codebase tracks
  the real tau-action on each basis element directly (as `tauPoly`), not
  just a summary `tautorsion` integer. If the basis-mismatch or ambiguous
  cases above ever need to be resolved with full certainty rather than left
  as "unknown", that's the place to get ground-truth factorizations rather
  than inferring further from these two CSVs alone.
