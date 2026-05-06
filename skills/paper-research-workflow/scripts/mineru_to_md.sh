#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: mineru_to_md.sh <input.pdf> --output <output-dir>" >&2
  exit 2
fi

if [[ -n "${MINERU_TO_MD:-}" ]]; then
  exec "${MINERU_TO_MD}" "$@"
fi

if command -v mineru >/dev/null 2>&1; then
  input=""
  output=""
  args=("$@")
  for ((i = 0; i < ${#args[@]}; i++)); do
    case "${args[$i]}" in
      --output)
        output="${args[$((i + 1))]:-}"
        ;;
      *)
        if [[ -z "$input" && "${args[$i]}" != --* ]]; then
          input="${args[$i]}"
        fi
        ;;
    esac
  done
  if [[ -z "$input" || -z "$output" ]]; then
    echo "mineru adapter requires <input> and --output <dir>" >&2
    exit 2
  fi
  exec mineru -p "$input" -o "$output"
fi

echo "No MinerU wrapper found. Set MINERU_TO_MD=/path/to/mineru_to_md.sh or install mineru on PATH." >&2
exit 127
