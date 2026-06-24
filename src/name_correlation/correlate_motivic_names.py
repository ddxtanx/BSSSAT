#!/usr/bin/env python3
"""Correlate element names between the C-motivic Adams E2 chart file
(Adams-motivic-E2.csv, human-readable names like "h0 d0") and the matching
machine-generated file (Adams-motivic-E2-machine.csv, names like "{a-b}").

Why this exists: find_differential.py works off Adams-motivic-E2.csv alone,
grouping by (stem, Adams filtration, weight, tautorsion). That file does not
carry the full h0/h1/h2/h3 extension data the machine file has, and the
machine file's generator names aren't the human-readable ones used elsewhere
in this project. This script produces a name<->name correspondence so the two
files can be cross-referenced.

IMPORTANT CAVEAT this script tries to detect rather than paper over: matching
purely by (stem, Adams filtration, weight, tautorsion) silently assumes the
chart's chosen basis for the vector space at that bidegree is literally a
renaming of the machine's chosen basis there. That's usually true, but not
always -- the two files can choose different bases for the same multi
-dimensional space, in which case an element's *individual* tautorsion value
is not a basis-independent fact. See detect_basis_mismatches() below: it
flags (stem, filtration, weight) slices where this is actually observed (the
total dimension agrees but the *multiset* of tautorsion values across the
slice does not), and routes everything there to its own report instead of
silently mismatching it or lumping it in with ordinary "no candidate" rows.

Matching strategy (for slices that pass the basis-mismatch check):

Pass 1 (key match): group rows by (stem, Adams filtration, weight,
tautorsion). A key with exactly one row on each side is an unambiguous match
-- there's only one basis vector in that 1-dimensional piece, so there's
nothing for a change of basis to mix it with.

Pass 2 (structural match): for keys with multiple candidates on at least one
side, use the h0/h1/h2 extension structure to disambiguate. A candidate pair
(chart row, machine row) is consistent only if they agree on which of
h0/h1/h2 extensions exist at all (empty vs. not), in both directions, AND --
for any target naming a single element that's already a confirmed key
match -- the translation agrees on the other side, checked both forward
(this row's own targets) and backward (which already-confirmed rows extend
INTO this row). A group resolves only when exactly one zero-contradiction
pairing exists among its candidates.

Deliberately NOT a fixed point: this pass only ever consults the Pass 1 key
matches, never another structural match. A structural match earlier in this
file's history could chain through other structural matches (occasionally 3
or 4 hops deep), and there's no way to audit a multi-hop chain's correctness
without re-deriving it -- a wrong link partway through silently propagates.
Restricting every structural match to a single hop from an unambiguous
dimension-1 key match means each one is directly checkable: "this specific
h_i edge connects this specific candidate to this specific certain match,"
full stop. This costs some matches that genuinely needed the deeper chain
(losing them is not an error, they fall into "ambiguous" instead), in
exchange for every accepted match being independently auditable.

An earlier version of this script also tried a "loose" rule that excused
chart-blank-but-machine-has-an-extension as a non-contradiction (since the
chart leaves most machine-confirmed extensions unannotated -- see
consistency_warning below). That rule is not used for matching: it traded
certainty for coverage, and "we need certainty" wins.

Whatever is still ambiguous after that, or has no candidate on the other side
at all (e.g. machine-only rows from periodic towers the chart collapses with
"loc"), is written to its own report rather than guessed at. The script
exits nonzero only if genuinely ambiguous groups (or basis-mismatch-suspected
slices) remain -- rows with no counterpart on the other side are expected and
are not treated as a failure.

Every row also gets a name_occurrence column. Chart names sometimes collide:
the same expression appears twice, distinguished only by the source data
appending " again" to the second one (e.g. "D2" / "D2 again"). These are
real, distinct elements, not duplicate data -- rather than dropping either
one, name_occurrence records, in order of appearance in the original CSV,
which occurrence a row is (1, 2, ...) of its base name (trailing " again"
stripped).

h3: the machine file has h3info/h3target; the chart file has no h3 column at
all. That means h3 *cannot* be used to cross-check a chart<->machine pairing
-- there's nothing on the chart side to compare it to. It's still useful
data, so matched rows carry it through as machine_h3info/machine_h3target
rather than silently dropping it.

Usage:
    python3 correlate_motivic_names.py
    python3 correlate_motivic_names.py --e2 path/to/Adams-motivic-E2.csv \\
        --machine path/to/Adams-motivic-E2-machine.csv --outdir out/

See README.md in this directory for input/output file details and current
known limitations.
"""
import argparse
import csv
import itertools
import os
from collections import Counter, defaultdict

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_E2_PATH = os.path.join(THIS_DIR, "..", "Adams-motivic-E2.csv")
DEFAULT_MACHINE_PATH = os.path.join(THIS_DIR, "..", "Adams-motivic-E2-machine.csv")

MATCHED_FILENAME = "Adams-motivic-name-correlation.csv"
AMBIGUOUS_FILENAME = "Adams-motivic-name-correlation-ambiguous.csv"
UNMATCHED_FILENAME = "Adams-motivic-name-correlation-unmatched.csv"
BASIS_MISMATCH_FILENAME = "Adams-motivic-name-correlation-basis-mismatch.csv"

EXT_FIELDS = ["h0target", "h1target", "h2target"]


def load_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def base_name(name):
    while name.endswith(" again"):
        name = name[: -len(" again")]
    return name


def annotate_occurrence(rows):
    seen = defaultdict(int)
    for row in rows:
        b = base_name(row["name"])
        seen[b] += 1
        row["name_occurrence"] = seen[b]


def key3_of(row):
    return (row["stem"], row["Adams filtration"], row["weight"])


def key4_of(row):
    return (row["stem"], row["Adams filtration"], row["weight"], row["tautorsion"])


def group_by(rows, key_fn):
    groups = defaultdict(list)
    for row in rows:
        groups[key_fn(row)].append(row)
    return groups


def detect_basis_mismatches(e2_rows, machine_rows):
    """(stem, filtration, weight) slices where the chart and machine sides
    have the same total dimension but DIFFERENT multisets of tautorsion
    values. This is a sign that the two files' chosen bases for that
    multi-dimensional slice are genuinely different (a real change of basis),
    not just a renaming -- see the module docstring. Returns the set of such
    3-field keys."""
    g2 = group_by(e2_rows, key3_of)
    gm = group_by(machine_rows, key3_of)
    suspects = set()
    for key in set(g2) & set(gm):
        e2_candidates, machine_candidates = g2[key], gm[key]
        if len(e2_candidates) != len(machine_candidates):
            continue  # dimension mismatch is handled separately (usually a computed-range gap)
        if Counter(r["tautorsion"] for r in e2_candidates) != Counter(r["tautorsion"] for r in machine_candidates):
            suspects.add(key)
    return suspects


def is_plain_name(value):
    """True if value names exactly one element: not empty, not the "loc"
    periodicity marker, and not a multi-term sum."""
    return value not in ("", "loc") and "+" not in value


def build_incoming(rows):
    """target name -> [(source name, ext), ...] for every row/ext whose
    target is a single plain name."""
    incoming = defaultdict(list)
    for row in rows:
        for ext in EXT_FIELDS:
            v = row[ext]
            if is_plain_name(v):
                incoming[v].append((row["name"], ext))
    return incoming


def pair_consistency(e2_row, machine_row, confirmed, incoming_e2, incoming_machine):
    """("contradiction"|"ok", evidence_count) for treating these two rows as
    the same element, given only the Pass 1 key matches (confirmed must never
    contain anything from Pass 2 itself -- see module docstring on why this
    pass deliberately isn't a fixed point).

    Chart and machine must agree on whether each h0/h1/h2 extension exists at
    all (empty vs. not) -- this is the "strict" rule; there used to also be a
    looser one and it's not used here anymore, see module docstring."""
    evidence = 0

    for ext in EXT_FIELDS:
        e_val, m_val = e2_row[ext], machine_row[ext]
        e_empty, m_empty = e_val == "", m_val == ""
        if e_empty != m_empty:
            return "contradiction", evidence
        if e_empty:
            continue
        if is_plain_name(e_val) and is_plain_name(m_val) and e_val in confirmed:
            if confirmed[e_val] == m_val:
                evidence += 1
            else:
                return "contradiction", evidence

    machine_incoming_by_ext = defaultdict(set)
    for src, ext in incoming_machine.get(machine_row["name"], []):
        machine_incoming_by_ext[ext].add(src)
    for src_name, ext in incoming_e2.get(e2_row["name"], []):
        if src_name in confirmed:
            if confirmed[src_name] in machine_incoming_by_ext[ext]:
                evidence += 1
            else:
                return "contradiction", evidence

    return "ok", evidence


def try_resolve_group(e2_candidates, machine_candidates, confirmed, incoming_e2, incoming_machine):
    """If exactly one zero-contradiction injection exists between the smaller
    and larger candidate list, return its (e2_row, machine_row) pairs."""
    if len(e2_candidates) <= len(machine_candidates):
        small, large, small_is_e2 = e2_candidates, machine_candidates, True
    else:
        small, large, small_is_e2 = machine_candidates, e2_candidates, False

    survivors = []
    for combo in itertools.permutations(large, len(small)):
        pairs = []
        contradiction = False
        for s_row, l_row in zip(small, combo):
            e2_row, machine_row = (s_row, l_row) if small_is_e2 else (l_row, s_row)
            verdict, _ = pair_consistency(e2_row, machine_row, confirmed, incoming_e2, incoming_machine)
            if verdict == "contradiction":
                contradiction = True
                break
            pairs.append((e2_row, machine_row))
        if not contradiction:
            survivors.append(pairs)

    if len(survivors) == 1:
        return survivors[0]
    return None


def has_extension_warning(e2_row, machine_row):
    """True if the chart claims a plain-name h0/h1/h2 extension that the
    machine row doesn't have at all. The reverse (chart blank, machine has
    it) is the chart's normal "not annotated" behavior and is not a
    warning -- see module docstring."""
    for ext in EXT_FIELDS:
        e_val, m_val = e2_row[ext], machine_row[ext]
        if is_plain_name(e_val) and m_val == "":
            return True
    return False


def report_row(key, side, row):
    stem, filtration, weight, tautorsion = key
    return {
        "stem": stem, "Adams filtration": filtration, "weight": weight,
        "tautorsion": tautorsion, "side": side, "name": row["name"],
        "name_occurrence": row["name_occurrence"],
    }


def correlate(e2_path, machine_path):
    e2_rows = load_rows(e2_path)
    machine_rows = load_rows(machine_path)

    annotate_occurrence(e2_rows)
    annotate_occurrence(machine_rows)

    suspect_keys = detect_basis_mismatches(e2_rows, machine_rows)

    basis_mismatch_sided_rows = []  # (side, row)
    e2_clean, machine_clean = [], []
    for row in e2_rows:
        if key3_of(row) in suspect_keys:
            basis_mismatch_sided_rows.append(("motivic", row))
        else:
            e2_clean.append(row)
    for row in machine_rows:
        if key3_of(row) in suspect_keys:
            basis_mismatch_sided_rows.append(("machine", row))
        else:
            machine_clean.append(row)

    e2_by_name = {r["name"]: r for r in e2_rows}
    machine_by_name = {r["name"]: r for r in machine_rows}

    e2_groups = group_by(e2_clean, key4_of)
    machine_groups = group_by(machine_clean, key4_of)
    all_keys = sorted(
        set(e2_groups) | set(machine_groups),
        key=lambda k: (int(k[0]), int(k[1]), int(k[2]), int(k[3])),
    )

    incoming_e2 = build_incoming(e2_clean)
    incoming_machine = build_incoming(machine_clean)

    confirmed = {}       # motivic (chart) name -> machine name
    matched_method = {}  # motivic name -> "key", "strict", or "loose"
    ambiguous_groups = []
    unmatched = []

    for key in all_keys:
        e2_candidates = e2_groups.get(key, [])
        machine_candidates = machine_groups.get(key, [])
        if not e2_candidates or not machine_candidates:
            for row in e2_candidates:
                unmatched.append(report_row(key, "motivic", row))
            for row in machine_candidates:
                unmatched.append(report_row(key, "machine", row))
            continue
        if len(e2_candidates) == 1 and len(machine_candidates) == 1:
            confirmed[e2_candidates[0]["name"]] = machine_candidates[0]["name"]
            matched_method[e2_candidates[0]["name"]] = "key"
        else:
            ambiguous_groups.append((key, e2_candidates, machine_candidates))

    key_match_count = len(confirmed)

    # Single pass only -- deliberately not a fixed point. Every structural
    # match below is checked against key_matches_only (frozen Pass-1 result),
    # never against another structural match, so no chain of inferences can
    # build up. See module docstring.
    key_matches_only = dict(confirmed)
    still_ambiguous = []
    for key, e2_candidates, machine_candidates in ambiguous_groups:
        result = try_resolve_group(e2_candidates, machine_candidates, key_matches_only, incoming_e2, incoming_machine)
        if result is None:
            still_ambiguous.append((key, e2_candidates, machine_candidates))
        else:
            for e2_row, machine_row in result:
                confirmed[e2_row["name"]] = machine_row["name"]
                matched_method[e2_row["name"]] = "structural"
    ambiguous_groups = still_ambiguous

    matched_rows = []
    for motivic_name, machine_name in confirmed.items():
        e2_row = e2_by_name[motivic_name]
        machine_row = machine_by_name[machine_name]
        matched_rows.append({
            "motivic_name": motivic_name,
            "machine_name": machine_name,
            "stem": e2_row["stem"],
            "Adams filtration": e2_row["Adams filtration"],
            "weight": e2_row["weight"],
            "tautorsion": e2_row["tautorsion"],
            "name_occurrence": e2_row["name_occurrence"],
            "match_method": matched_method[motivic_name],
            "consistency_warning": has_extension_warning(e2_row, machine_row),
            "machine_h3info": machine_row["h3info"],
            "machine_h3target": machine_row["h3target"],
        })
    matched_rows.sort(key=lambda r: (int(r["stem"]), int(r["Adams filtration"]), int(r["weight"])))

    ambiguous_rows = []
    for key, e2_candidates, machine_candidates in ambiguous_groups:
        for row in e2_candidates:
            ambiguous_rows.append(report_row(key, "motivic", row))
        for row in machine_candidates:
            ambiguous_rows.append(report_row(key, "machine", row))
    ambiguous_rows.sort(key=lambda r: (int(r["stem"]), int(r["Adams filtration"]), int(r["weight"])))

    unmatched.sort(key=lambda r: (int(r["stem"]), int(r["Adams filtration"]), int(r["weight"])))

    basis_mismatch_report = [
        report_row(key4_of(row), side, row) for side, row in basis_mismatch_sided_rows
    ]
    basis_mismatch_report.sort(key=lambda r: (int(r["stem"]), int(r["Adams filtration"]), int(r["weight"])))

    method_counts = Counter(matched_method.values())
    stats = {
        "key_match_count": method_counts.get("key", 0),
        "structural_match_count": method_counts.get("structural", 0),
        "consistency_warning_count": sum(1 for r in matched_rows if r["consistency_warning"]),
        "ambiguous_group_count": len(ambiguous_groups),
        "basis_mismatch_slice_count": len(suspect_keys),
    }
    return matched_rows, ambiguous_rows, unmatched, basis_mismatch_report, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--e2", default=DEFAULT_E2_PATH, help="Path to Adams-motivic-E2.csv")
    parser.add_argument("--machine", default=DEFAULT_MACHINE_PATH, help="Path to Adams-motivic-E2-machine.csv")
    parser.add_argument("--outdir", default=".", help="Directory to write the output CSVs into")
    args = parser.parse_args()

    matched_rows, ambiguous_rows, unmatched, basis_mismatch_rows, stats = correlate(args.e2, args.machine)

    os.makedirs(args.outdir, exist_ok=True)
    matched_path = os.path.join(args.outdir, MATCHED_FILENAME)
    ambiguous_path = os.path.join(args.outdir, AMBIGUOUS_FILENAME)
    unmatched_path = os.path.join(args.outdir, UNMATCHED_FILENAME)
    basis_mismatch_path = os.path.join(args.outdir, BASIS_MISMATCH_FILENAME)

    with open(matched_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "motivic_name", "machine_name", "stem", "Adams filtration", "weight",
            "tautorsion", "name_occurrence", "match_method", "consistency_warning",
            "machine_h3info", "machine_h3target",
        ])
        writer.writeheader()
        writer.writerows(matched_rows)

    with open(ambiguous_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "stem", "Adams filtration", "weight", "tautorsion", "side", "name",
            "name_occurrence",
        ])
        writer.writeheader()
        writer.writerows(ambiguous_rows)

    with open(unmatched_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "stem", "Adams filtration", "weight", "tautorsion", "side", "name",
            "name_occurrence",
        ])
        writer.writeheader()
        writer.writerows(unmatched)

    with open(basis_mismatch_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "stem", "Adams filtration", "weight", "tautorsion", "side", "name",
            "name_occurrence",
        ])
        writer.writeheader()
        writer.writerows(basis_mismatch_rows)

    print(f"Matched by (stem, filtration, weight, tautorsion) alone: {stats['key_match_count']}")
    print(f"Matched via h0/h1/h2 structure (single hop from a key match only): {stats['structural_match_count']}")
    print(f"Total matched: {len(matched_rows)} ({stats['consistency_warning_count']} with a consistency_warning)")
    print(f"Rows still in ambiguous groups: {len(ambiguous_rows)} ({stats['ambiguous_group_count']} keys)")
    print(f"Rows with no candidate on the other side (not an error): {len(unmatched)}")
    print(f"Rows excluded as basis-mismatch-suspected: {len(basis_mismatch_rows)} ({stats['basis_mismatch_slice_count']} slices)")
    print(f"Wrote: {matched_path}, {ambiguous_path}, {unmatched_path}, {basis_mismatch_path}")

    if stats["ambiguous_group_count"] or stats["basis_mismatch_slice_count"]:
        raise SystemExit(
            f"FAILED: {stats['ambiguous_group_count']} keys remain ambiguous after structural "
            f"matching, and {stats['basis_mismatch_slice_count']} (stem, filtration, weight) "
            f"slices show a real basis mismatch between the two files. See {ambiguous_path} "
            f"and {basis_mismatch_path}."
        )


if __name__ == "__main__":
    main()
