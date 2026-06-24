#!/usr/bin/env python3
"""For every machine-named generator in Adams-motivic-E2-machine.csv, determine
whether it is h1-periodic, h1-torsion, or unknown, using the chart file's
h1target column (h1target == "loc" means h1-periodic) together with the
chart<->machine correlation from correlate_motivic_names.py.

Three ways a machine generator's status gets determined:

1. matched -- correlate_motivic_names resolved this machine name to exactly
   one chart name (via key or structural matching). Status comes directly
   from that chart row's h1target.
2. ambiguous-unanimous -- correlate_motivic_names could not resolve which
   chart candidate this machine generator corresponds to, but *every* chart
   candidate in that bidegree group has the same h1-periodicity status. Since
   the true correspondence is some one of them, the status is determined
   either way.
3. ambiguous-mixed / no-chart-candidate -- otherwise: either the candidates
   disagree (some periodic, some not) so we can't tell which applies here, or
   there's no chart candidate at all for this machine generator's bidegree
   (typical for periodic-tower continuations the chart collapses into a
   single "loc" entry). Status is "unknown" either way; `basis` distinguishes
   the two cases.

Usage:
    python3 classify_h1_periodicity.py
    python3 classify_h1_periodicity.py --e2 PATH --machine PATH --outdir out/
"""
import argparse
import csv
import os
from collections import defaultdict

from correlate_motivic_names import (
    DEFAULT_E2_PATH,
    DEFAULT_MACHINE_PATH,
    correlate,
    key_of,
    load_rows,
)

OUTPUT_FILENAME = "Adams-motivic-h1-periodicity.csv"


def h1_status_of(e2_row):
    return "h1-periodic" if e2_row["h1target"] == "loc" else "h1-torsion"


def classify(e2_path, machine_path):
    e2_rows = load_rows(e2_path)
    machine_rows = load_rows(machine_path)
    e2_by_name = {r["name"]: r for r in e2_rows}

    matched_rows, ambiguous_rows, _unmatched, _stats = correlate(e2_path, machine_path)

    machine_to_match = {r["machine_name"]: r for r in matched_rows}

    key_to_motivic_names = defaultdict(list)
    key_to_machine_names = defaultdict(list)
    for r in ambiguous_rows:
        key = (r["stem"], r["Adams filtration"], r["weight"], r["tautorsion"])
        if r["side"] == "motivic":
            key_to_motivic_names[key].append(r["name"])
        else:
            key_to_machine_names[key].append(r["name"])
    machine_name_to_ambiguous_key = {
        name: key for key, names in key_to_machine_names.items() for name in names
    }

    output_rows = []
    for machine_row in machine_rows:
        name = machine_row["name"]

        if name in machine_to_match:
            match = machine_to_match[name]
            status = h1_status_of(e2_by_name[match["motivic_name"]])
            basis = f"matched ({match['match_method']})"
            candidates = match["motivic_name"]
        elif name in machine_name_to_ambiguous_key:
            key = machine_name_to_ambiguous_key[name]
            motivic_candidates = key_to_motivic_names[key]
            statuses = {h1_status_of(e2_by_name[n]) for n in motivic_candidates}
            candidates = ";".join(motivic_candidates)
            if len(statuses) == 1:
                status, basis = next(iter(statuses)), "ambiguous-unanimous"
            else:
                status, basis = "unknown", "ambiguous-mixed"
        else:
            status, basis, candidates = "unknown", "no-chart-candidate", ""

        output_rows.append({
            "machine_name": name,
            "stem": machine_row["stem"],
            "Adams filtration": machine_row["Adams filtration"],
            "weight": machine_row["weight"],
            "tautorsion": machine_row["tautorsion"],
            "h1_status": status,
            "basis": basis,
            "motivic_names": candidates,
        })

    output_rows.sort(key=lambda r: (int(r["stem"]), int(r["Adams filtration"]), int(r["weight"])))
    return output_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--e2", default=DEFAULT_E2_PATH, help="Path to Adams-motivic-E2.csv")
    parser.add_argument("--machine", default=DEFAULT_MACHINE_PATH, help="Path to Adams-motivic-E2-machine.csv")
    parser.add_argument("--outdir", default=".", help="Directory to write the output CSV into")
    args = parser.parse_args()

    output_rows = classify(args.e2, args.machine)

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, OUTPUT_FILENAME)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "machine_name", "stem", "Adams filtration", "weight", "tautorsion",
            "h1_status", "basis", "motivic_names",
        ])
        writer.writeheader()
        writer.writerows(output_rows)

    status_counts = defaultdict(int)
    basis_counts = defaultdict(int)
    for r in output_rows:
        status_counts[r["h1_status"]] += 1
        basis_counts[r["basis"]] += 1

    print(f"Total machine generators classified: {len(output_rows)}")
    for status in ("h1-periodic", "h1-torsion", "unknown"):
        print(f"  {status}: {status_counts.get(status, 0)}")
    print("Basis breakdown:")
    for basis, count in sorted(basis_counts.items()):
        print(f"  {basis}: {count}")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
