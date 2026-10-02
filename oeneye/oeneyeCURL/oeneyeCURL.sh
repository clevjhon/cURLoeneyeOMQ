#!/usr/bin/env bash
#
# oeneyeCURL — a curl wrapper that knows the OENEYE OS Project's assets by
# name, so build scripts (and people) can fetch them without memorizing
# Zenodo record IDs and file paths.
#
# Zenodo:  DIY distro logo  https://doi.org/10.5281/zenodo.22973347
# License: CC-BY-4.0
# Curatorium / OENEYE OS Project
#
# Usage:
#   ./oeneyeCURL <asset> [output-path]
#   ./oeneyeCURL list
#   ./oeneyeCURL about | doi | cite | help
#
# Examples:
#   ./oeneyeCURL logo                     # -> ./oeneye-logo.png
#   ./oeneyeCURL logo /tmp/logo.png        # custom output path
#   ./oeneyeCURL wg-server                 # -> ./oeneye-wg-server.zip
#   ./oeneyeCURL distro-logo               # -> ./oeneye-distro-logo.zip
#
set -euo pipefail

VERSION="0.1.0"
DOI="10.5281/zenodo.22973347"
ZENODO="https://doi.org/${DOI}"

# ---- known assets (name -> "url|default-output-filename") ----------------
declare -A ASSETS=(
    [logo]="https://zenodo.org/records/22973195/files/1789571854667.png?download=1|oeneye-logo.png"
    [wg-server]="https://zenodo.org/records/22973347/files/oeneye-wg-server.zip?download=1|oeneye-wg-server.zip"
    [distro-logo]="https://zenodo.org/records/22973347/files/oeneye-distro-logo.zip?download=1|oeneye-distro-logo.zip"
)

print_banner() {
    echo "oeneyeCURL ${VERSION} — OENEYE OS Project asset fetcher"
    echo "Zenodo: ${ZENODO}"
    echo
}

cmd_about() {
    print_banner
    cat <<EOF
oeneyeCURL fetches named OENEYE OS Project assets (logo, scripts, plates)
from their canonical Zenodo locations, without callers needing to know
record IDs or exact filenames. It's a thin wrapper around curl — nothing
more; think of it as a lookup table plus a download.

Citation:
  Ketelhut, K. O. (2026). DIY distro logo. Zenodo. ${ZENODO}
EOF
}

cmd_doi() {
    echo "${DOI}"
}

cmd_cite() {
    cat <<EOF
@misc{oeneyecurl2026,
  author    = {Ketelhut, Kai Olaf},
  title     = {DIY distro logo (oeneyeCURL asset registry)},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {${DOI}},
  url       = {${ZENODO}},
  note      = {Curatorium / OENEYE OS Project. org-curatorium community. CC-BY-4.0}
}
EOF
}

cmd_list() {
    echo "Known assets:"
    for name in "${!ASSETS[@]}"; do
        local url="${ASSETS[$name]%%|*}"
        printf "  %-14s %s\n" "${name}" "${url}"
    done
}

cmd_help() {
    print_banner
    cat <<EOF
Usage: $(basename "$0") <command> [args]

Commands:
  <asset> [out]   fetch a known asset (see 'list'); optional custom output path
  list            show all known assets and their source URLs
  about           project identity and citation blurb
  doi             print DOI only
  cite            print BibTeX stub
  help            this help
EOF
}

cmd_fetch() {
    local name="$1"
    local out="${2:-}"

    if [[ -z "${ASSETS[$name]+x}" ]]; then
        echo "oeneyeCURL: unknown asset '${name}'" >&2
        echo "Run '$(basename "$0") list' to see known assets." >&2
        exit 1
    fi

    local entry="${ASSETS[$name]}"
    local url="${entry%%|*}"
    local default_out="${entry##*|}"
    out="${out:-${default_out}}"

    if ! command -v curl >/dev/null 2>&1; then
        echo "oeneyeCURL: curl is required but not installed" >&2
        exit 1
    fi

    echo "==> Fetching '${name}' -> ${out}"
    curl -fL --progress-bar -o "${out}" "${url}"
    echo "==> Done: ${out}"
}

# ---- dispatch ---------------------------------------------------------
if [ $# -lt 1 ]; then
    cmd_help
    exit 1
fi

case "$1" in
    about) cmd_about ;;
    doi)   cmd_doi ;;
    cite)  cmd_cite ;;
    list)  cmd_list ;;
    help|-h|--help) cmd_help ;;
    *)     cmd_fetch "$1" "${2:-}" ;;
esac
