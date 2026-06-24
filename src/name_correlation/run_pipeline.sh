#!/usr/bin/env bash
# Downloads the two Isaksen-Wang-Xu Adams chart CSVs this directory's scripts
# need (if not already present next to this script's parent, src/), then runs
# the correlation and h1-periodicity classification scripts.
#
# Source: "Classical and C-motivic Adams charts" data files,
# DOI 10.5281/zenodo.6987157 (cited in README-Adams.pdf at the repo root of
# that dataset). Downloaded via the Zenodo REST API, which serves each file's
# content at a stable URL keyed by record ID and filename, and is verified
# against the checksum Zenodo reports for that file.
#
# Usage: ./run_pipeline.sh [outdir]
#   outdir defaults to ./out

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTDIR="${1:-$SCRIPT_DIR/out}"

ZENODO_RECORD=6987157
ZENODO_BASE="https://zenodo.org/api/records/$ZENODO_RECORD/files"

E2_CSV="$SRC_DIR/Adams-motivic-E2.csv"
MACHINE_CSV="$SRC_DIR/Adams-motivic-E2-machine.csv"
E2_MD5="2316d8157e285d027531e153127b3a53"
MACHINE_MD5="e334e1662b6080f40858f02dba8b19a9"

md5_of() {
  if command -v md5sum >/dev/null 2>&1; then
    md5sum "$1" | awk '{print $1}'
  else
    md5 -q "$1"
  fi
}

ensure_csv() {
  local path="$1" filename="$2" expected_md5="$3"
  if [ -f "$path" ]; then
    local actual_md5
    actual_md5="$(md5_of "$path")"
    if [ "$actual_md5" = "$expected_md5" ]; then
      echo "Found $filename (checksum OK), skipping download."
      return
    fi
    echo "WARNING: $filename exists but checksum doesn't match the expected" \
         "Zenodo record $ZENODO_RECORD file. Re-downloading." >&2
  fi
  echo "Downloading $filename from Zenodo record $ZENODO_RECORD..."
  curl -fSL "$ZENODO_BASE/$filename/content" -o "$path"
  local actual_md5
  actual_md5="$(md5_of "$path")"
  if [ "$actual_md5" != "$expected_md5" ]; then
    echo "ERROR: downloaded $filename but checksum doesn't match" \
         "(expected $expected_md5, got $actual_md5). Aborting." >&2
    exit 1
  fi
}

ensure_csv "$E2_CSV" "Adams-motivic-E2.csv" "$E2_MD5"
ensure_csv "$MACHINE_CSV" "Adams-motivic-E2-machine.csv" "$MACHINE_MD5"

mkdir -p "$OUTDIR"

echo
echo "== Running correlate_motivic_names.py =="
python3 "$SCRIPT_DIR/correlate_motivic_names.py" --e2 "$E2_CSV" --machine "$MACHINE_CSV" --outdir "$OUTDIR" || true
# (exits nonzero if any keys remain ambiguous after structural matching --
# that's expected/known, see README.md, so don't let it abort the pipeline)

echo
echo "== Running classify_h1_periodicity.py =="
python3 "$SCRIPT_DIR/classify_h1_periodicity.py" --e2 "$E2_CSV" --machine "$MACHINE_CSV" --outdir "$OUTDIR"

echo
echo "Done. Output written to $OUTDIR"
