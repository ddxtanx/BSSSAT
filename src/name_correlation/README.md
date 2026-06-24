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
bloating the repo with another ~500KB data file). Download
`Adams-motivic-E2-machine.csv` from the Zenodo record above and place it next
to `Adams-motivic-E2.csv`, or pass `--machine` pointing wherever you put it.

## Usage

```
python3 correlate_motivic_names.py
python3 correlate_motivic_names.py --e2 PATH --machine PATH --outdir out/
```

Run with no arguments, it looks for both CSVs in `src/` (one level up from
this script) and writes output into the current directory.

## How matching works

1. **Key match**: group rows by `(stem, Adams filtration, weight,
   tautorsion)`. A key with exactly one row on each side is a direct match.
2. **Structural match**: for keys with multiple candidates on either side
   (about 313 of ~3860 chart rows, before this pass), use the h0/h1/h2
   extension targets to disambiguate. A candidate pairing is only accepted if
   it's the *unique* zero-contradiction pairing in its group — both forward
   (this element's own extension targets) and backward (what other,
   already-resolved elements extend into it) are checked. This runs to a
   fixed point, since resolving one group can supply the translations needed
   to resolve another.

Both passes are conservative: a group is only resolved when there's exactly
one assignment consistent with everything confirmed so far. Anything else is
reported, not guessed at.

## Output

Three CSVs, written to `--outdir` (default: current directory):

- **Adams-motivic-name-correlation.csv** — resolved `motivic_name <->
  machine_name` pairs, with `match_method` (`key` or `structural`) so you can
  tell how confident each pairing is.
- **Adams-motivic-name-correlation-ambiguous.csv** — rows belonging to a key
  where multiple candidates remain on at least one side even after
  structural matching, i.e. we genuinely can't tell which is which.
- **Adams-motivic-name-correlation-unmatched.csv** — rows with *no*
  candidate at all on the other side. Mostly machine-file rows from
  `h0`/`h1`-periodic towers that the chart file collapses into a single `loc`
  entry; this is expected and not a sign of a problem.

Every row in all three files has a `name_occurrence` column. Chart names
occasionally collide — the same expression is reused for two genuinely
different elements, distinguished in the source data only by appending
`" again"` to the second one's name (e.g. `D2` / `D2 again`). These are kept
as separate, real rows rather than deduplicated; `name_occurrence` records,
in file order, which occurrence (1, 2, ...) of its base name a row is, so the
collision is explicit instead of silent.

## Known limitations (as of this writing, full computed range)

- ~178 keys (~690 rows) remain ambiguous even after structural matching —
  mostly cases where the candidate counts don't match between the two files
  (e.g. one chart name vs. several machine generators), so no bijection
  exists to even attempt.
- A handful of the remaining ambiguous groups mix an h1-periodic candidate
  with a non-periodic one at the same bidegree; these look like edge-of
  -computed-range effects (the machine computation may not extend far enough
  to confirm the periodic continuation the chart already asserts via `loc`)
  rather than a labeling bug worth chasing further.
