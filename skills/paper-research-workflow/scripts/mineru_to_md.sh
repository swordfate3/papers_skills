#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: mineru_to_md.sh <input.pdf> --output <output-dir> [--backend auto|custom|local|standard-cloud|agent-cloud]" >&2
  exit 2
fi

input=""
output=""
backend="${MINERU_BACKEND:-auto}"
args=("$@")
for ((i = 0; i < ${#args[@]}; i++)); do
  case "${args[$i]}" in
    --output)
      output="${args[$((i + 1))]:-}"
      ;;
    --backend|--mineru-backend)
      backend="${args[$((i + 1))]:-auto}"
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

if [[ "$backend" == "custom" || ( "$backend" == "auto" && -n "${MINERU_TO_MD:-}" ) ]]; then
  if [[ -z "${MINERU_TO_MD:-}" ]]; then
    echo "MINERU_TO_MD is required for custom MinerU backend." >&2
    exit 127
  fi
  exec "${MINERU_TO_MD}" "$@"
fi

if [[ "$backend" == "standard-cloud" || "$backend" == "agent-cloud" || ( "$backend" == "auto" && -n "${MINERU_TOKEN:-}" ) ]]; then
  exec python "$(dirname "$0")/mineru_cloud_cli.py" "$input" --output "$output" --backend "$backend"
fi

if [[ "$backend" == "local" || "$backend" == "auto" ]]; then
  if command -v mineru >/dev/null 2>&1; then
    exec mineru -p "$input" -o "$output"
  fi
fi

if [[ "$backend" == "auto" ]]; then
  exec python "$(dirname "$0")/mineru_cloud_cli.py" "$input" --output "$output" --backend agent-cloud
fi

echo "No MinerU backend found. Configure MINERU_TOKEN, set MINERU_TO_MD, use --backend agent-cloud, or install mineru on PATH." >&2
exit 127
