#!/usr/bin/env bash
# Fetch the HEC reading list (SPEC.md §10) + ancillary data files.
# PDFs land in papers/, source tarballs (for ancillary data) in papers/src/,
# extracted ancillary data in data/raw/<arxiv-id>/.
# papers/ and data/raw/ are gitignored; this script is the manifest.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p papers/src data/raw

# id : short label (label is informational only)
PAPERS=(
  "1005.3035:van-raamsdonk-spacetime-from-entanglement"
  "1505.07839:bnossw-holographic-entropy-cone"
  "1903.09148:hernandez-cuenca-5-party-cone"
  "2412.15364:he-hubeny-rota-6-party-extreme-rays"
  "2309.06296:czech-et-al-inequality-harvest"
  "2403.13283:bao-naskar-deterministic-contraction-maps"
  "2409.17317:bao-furuya-naskar-partial-cubes"
  "2506.18086:contraction-map-completeness"
  "2204.00075:marginal-independence-tree-conjecture"
  "2412.18018:hubeny-rota-correlation-hypergraph"
  "2512.18702:hubeny-rota-tree-construction-algorithm"
  "2512.24490:hubeny-rota-chordality-sufficient"
  "2601.19979:he-lee-ooguri-rl-mystery-realizations"
)

# Papers with arXiv ancillary data files (shipped inside the source tarball)
ANCILLARY=("2412.15364" "2309.06296")

fail=0
for entry in "${PAPERS[@]}"; do
  id="${entry%%:*}"
  out="papers/${id}.pdf"
  if [[ ! -s "$out" ]]; then
    echo "PDF  $id"
    curl -sL --max-time 120 -o "$out" "https://arxiv.org/pdf/${id}" || { echo "FAIL pdf $id"; fail=1; }
    sleep 2
  fi
done

for id in "${ANCILLARY[@]}"; do
  src="papers/src/${id}.tar.gz"
  if [[ ! -s "$src" ]]; then
    echo "SRC  $id"
    curl -sL --max-time 180 -o "$src" "https://arxiv.org/e-print/${id}" || { echo "FAIL src $id"; fail=1; continue; }
    sleep 2
  fi
  mkdir -p "data/raw/${id}"
  # e-print may be gzipped tar or a bare gzipped TeX file; try tar first
  tar -xzf "$src" -C "data/raw/${id}" 2>/dev/null || \
    tar -xf "$src" -C "data/raw/${id}" 2>/dev/null || \
    echo "NOTE $id: e-print is not a tarball, left as-is in papers/src/"
done

# He-Hubeny-Rota ray data, pinned to the snapshot all results were computed
# against (see README "Data & references")
ROTA_COMMIT="e973df6e0aa6d1c8e551b13f1998defdd24e2686"
if [[ ! -s data/raw/rota/n6_rays.txt ]]; then
  echo "DATA rota extreme-ray repository @ ${ROTA_COMMIT:0:12}"
  tmp=$(mktemp -d)
  git clone -q https://github.com/Max-Rota/SSA-compatible-Extreme-Rays-of-the-Subadditivity-Cone "$tmp" \
    && git -C "$tmp" checkout -q "$ROTA_COMMIT" \
    && mkdir -p data/raw/rota \
    && cp "$tmp"/n=6/rays.txt data/raw/rota/n6_rays.txt \
    && cp "$tmp"/n=5/rays.txt data/raw/rota/n5_rays.txt \
    && cp "$tmp"/README.md data/raw/rota/ \
    || { echo "FAIL rota data"; fail=1; }
  rm -rf "$tmp"
fi

echo "--- summary ---"
ls -la papers/*.pdf 2>/dev/null | awk '{print $5, $9}'
for id in "${ANCILLARY[@]}"; do
  echo "ancillary ${id}:"
  find "data/raw/${id}" -maxdepth 2 -name '*' -type d | head -5
  find "data/raw/${id}" -iname '*anc*' -maxdepth 1 -type d -exec ls {} \; 2>/dev/null | head -20
done
exit $fail
