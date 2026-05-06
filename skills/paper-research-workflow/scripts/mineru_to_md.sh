#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: mineru_to_md.sh <input.pdf> --output <output-dir> [--backend auto|local|standard-cloud|agent-cloud]" >&2
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

if [[ "$backend" == "standard-cloud" || "$backend" == "agent-cloud" || ( "$backend" == "auto" && -n "${MINERU_TOKEN:-}" ) ]]; then
  exec python "$(dirname "$0")/mineru_cloud_cli.py" "$input" --output "$output" --backend "$backend"
fi

if [[ "$backend" == "local" || "$backend" == "auto" ]]; then
  local_wrapper="$(dirname "$0")/mineru_local_docker.sh"
  if [[ -x "$local_wrapper" ]]; then
    if "$local_wrapper" status >/dev/null 2>&1; then
      exec "$local_wrapper" run "$input" --output "$output"
    fi
  fi
  if command -v mineru >/dev/null 2>&1; then
    exec mineru -p "$input" -o "$output"
  fi
fi

if [[ "$backend" == "auto" ]]; then
  exec python "$(dirname "$0")/mineru_cloud_cli.py" "$input" --output "$output" --backend agent-cloud
fi

echo "No MinerU backend found. Configure MINERU_TOKEN, use --backend agent-cloud, install mineru on PATH, or enable local Docker MinerU with python $(dirname "$0")/paper_workflow.py local-mineru --enable ." >&2
exit 127
