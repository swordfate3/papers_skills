#!/usr/bin/env bash
set -euo pipefail

DEFAULT_IMAGE="${MINERU_IMAGE:-mineru:latest}"
DEFAULT_DOCKER_DIR="${MINERU_DOCKER_DIR:-$HOME/docker_files/mineru}"
DEFAULT_DOCKERFILE_URL="${MINERU_DOCKERFILE_URL:-https://raw.githubusercontent.com/opendatalab/MinerU/master/docker/global/Dockerfile}"

usage() {
  cat <<'USAGE'
Usage:
  mineru_local_docker.sh <command> [options]

Commands:
  status
      Show whether docker exists and whether the MinerU image is ready.

  enable [--image IMAGE] [--docker-dir DIR]
      Build the MinerU Docker image locally.
      If DIR is missing, the script can download a Dockerfile from --dockerfile-url.

  run [options] <input-file-or-directory>
      Convert a local file with the built MinerU Docker image.

Run options:
  -o, --output DIR
  --image IMAGE
  --docker-dir DIR
  --dockerfile-url URL
  --no-build
  --no-gpu
  --dry-run
  -b, --backend BACKEND
  -m, --method METHOD
  -l, --lang LANG
  -u, --url URL
  --api-url URL
  -s, --start PAGE
  -e, --end PAGE
  -f, --formula BOOLEAN
  -t, --table BOOLEAN
USAGE
}

die() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

quote_cmd() {
  local quoted=()
  local arg
  for arg in "$@"; do
    quoted+=("$(printf '%q' "$arg")")
  done
  printf '%s\n' "${quoted[*]}"
}

abs_path() {
  local path="$1"
  if command -v realpath >/dev/null 2>&1; then
    realpath "$path"
  else
    (
      cd "$(dirname "$path")"
      printf '%s/%s\n' "$PWD" "$(basename "$path")"
    )
  fi
}

abs_dir_path() {
  local path="$1"
  local parent
  local leaf

  if [[ -d "$path" ]]; then
    abs_path "$path"
    return
  fi

  parent="$(dirname "$path")"
  leaf="$(basename "$path")"
  [[ -d "$parent" ]] || mkdir -p "$parent"
  (
    cd "$parent"
    printf '%s/%s\n' "$PWD" "$leaf"
  )
}

docker_image_ready() {
  docker image inspect "$1" >/dev/null 2>&1
}

print_status() {
  local image="$1"
  if ! command -v docker >/dev/null 2>&1; then
    printf '{\n  "docker_installed": false,\n  "docker_daemon_running": false,\n  "image_ready": false,\n  "image": "%s"\n}\n' "$image"
    return 1
  fi

  if ! docker info >/dev/null 2>&1; then
    printf '{\n  "docker_installed": true,\n  "docker_daemon_running": false,\n  "image_ready": false,\n  "image": "%s"\n}\n' "$image"
    return 1
  fi

  if docker_image_ready "$image"; then
    printf '{\n  "docker_installed": true,\n  "docker_daemon_running": true,\n  "image_ready": true,\n  "image": "%s"\n}\n' "$image"
    return 0
  fi

  printf '{\n  "docker_installed": true,\n  "docker_daemon_running": true,\n  "image_ready": false,\n  "image": "%s"\n}\n' "$image"
  return 1
}

build_image() {
  local image="$1"
  local docker_dir="$2"
  local dockerfile_url="$3"

  command -v docker >/dev/null 2>&1 || die "docker command not found"
  docker info >/dev/null 2>&1 || die "docker daemon is not running"

  if [[ ! -f "$docker_dir/Dockerfile" ]]; then
    mkdir -p "$docker_dir"
    command -v curl >/dev/null 2>&1 || die "curl command not found"
    curl -fsSL "$dockerfile_url" -o "$docker_dir/Dockerfile"
  fi

  docker build -t "$image" "$docker_dir"
}

run_conversion() {
  local image="$DEFAULT_IMAGE"
  local docker_dir="$DEFAULT_DOCKER_DIR"
  local dockerfile_url="$DEFAULT_DOCKERFILE_URL"
  local output_dir=""
  local input_path=""
  local should_build=0
  local use_gpu=1
  local dry_run=0
  local backend=""
  local method=""
  local lang=""
  local server_url=""
  local api_url=""
  local start_page=""
  local end_page=""
  local formula=""
  local table=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -o|--output)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        output_dir="$2"
        shift 2
        ;;
      --image)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        image="$2"
        shift 2
        ;;
      --docker-dir)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        docker_dir="$2"
        shift 2
        ;;
      --dockerfile-url)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        dockerfile_url="$2"
        shift 2
        ;;
      --no-build)
        should_build=0
        shift
        ;;
      --build)
        should_build=1
        shift
        ;;
      --no-gpu)
        use_gpu=0
        shift
        ;;
      --gpu)
        use_gpu=1
        shift
        ;;
      --dry-run)
        dry_run=1
        shift
        ;;
      -b|--backend)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        backend="$2"
        shift 2
        ;;
      -m|--method)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        method="$2"
        shift 2
        ;;
      -l|--lang)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        lang="$2"
        shift 2
        ;;
      -u|--url)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        server_url="$2"
        shift 2
        ;;
      --api-url)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        api_url="$2"
        shift 2
        ;;
      -s|--start)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        start_page="$2"
        shift 2
        ;;
      -e|--end)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        end_page="$2"
        shift 2
        ;;
      -f|--formula)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        formula="$2"
        shift 2
        ;;
      -t|--table)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        table="$2"
        shift 2
        ;;
      -*)
        die "Unknown option: $1"
        ;;
      *)
        [[ -z "$input_path" ]] || die "Only one input path is supported"
        input_path="$1"
        shift
        ;;
    esac
  done

  [[ -n "$input_path" ]] || die "Input path is required"
  [[ -e "$input_path" ]] || die "Input path not found: $input_path"

  input_abs="$(abs_path "$input_path")"
  if [[ -z "$output_dir" ]]; then
    input_name="$(basename "$input_abs")"
    output_dir="$PWD/mineru-md-output/${input_name%.*}"
  fi
  output_abs="$(abs_dir_path "$output_dir")"
  mkdir -p "$output_abs"

  if [[ "$use_gpu" -eq 0 && -z "$backend" ]]; then
    backend="pipeline"
  fi

  if [[ -f "$input_abs" ]]; then
    input_mount="$(dirname "$input_abs")"
    input_container="/data/input/$(basename "$input_abs")"
  else
    input_mount="$input_abs"
    input_container="/data/input"
  fi

  command -v docker >/dev/null 2>&1 || die "docker command not found"

  if ! docker_image_ready "$image"; then
    [[ "$should_build" -eq 1 ]] || die "Docker MinerU image not ready. Run status first, then ask the user whether to enable it."
    build_image "$image" "$docker_dir" "$dockerfile_url"
  fi

  docker_cmd=(docker run --rm)
  if [[ "$use_gpu" -eq 1 ]]; then
    docker_cmd+=(--gpus all --ipc host --ulimit memlock=-1 --ulimit stack=67108864)
  fi
  docker_cmd+=(
    -e MINERU_MODEL_SOURCE=local
    -v "$input_mount:/data/input:ro"
    -v "$output_abs:/data/output"
    "$image"
    mineru
    -p "$input_container"
    -o /data/output
  )

  [[ -n "$api_url" ]] && docker_cmd+=(--api-url "$api_url")
  [[ -n "$method" ]] && docker_cmd+=(-m "$method")
  [[ -n "$backend" ]] && docker_cmd+=(-b "$backend")
  [[ -n "$lang" ]] && docker_cmd+=(-l "$lang")
  [[ -n "$server_url" ]] && docker_cmd+=(-u "$server_url")
  [[ -n "$start_page" ]] && docker_cmd+=(-s "$start_page")
  [[ -n "$end_page" ]] && docker_cmd+=(-e "$end_page")
  [[ -n "$formula" ]] && docker_cmd+=(-f "$formula")
  [[ -n "$table" ]] && docker_cmd+=(-t "$table")

  if [[ "$dry_run" -eq 1 ]]; then
    printf 'Dry run command:\n%s\n' "$(quote_cmd "${docker_cmd[@]}")"
    return 0
  fi

  printf 'Running local Docker MinerU conversion...\n'
  printf '%s\n' "$(quote_cmd "${docker_cmd[@]}")"
  "${docker_cmd[@]}"
}

main() {
  [[ $# -ge 1 ]] || { usage >&2; exit 2; }

  local command="$1"
  shift

  case "$command" in
    status)
      local image="$DEFAULT_IMAGE"
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --image)
            [[ $# -ge 2 ]] || die "$1 requires a value"
            image="$2"
            shift 2
            ;;
          *)
            die "Unknown option for status: $1"
            ;;
        esac
      done
      print_status "$image"
      ;;
    enable)
      local image="$DEFAULT_IMAGE"
      local docker_dir="$DEFAULT_DOCKER_DIR"
      local dockerfile_url="$DEFAULT_DOCKERFILE_URL"
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --image)
            [[ $# -ge 2 ]] || die "$1 requires a value"
            image="$2"
            shift 2
            ;;
          --docker-dir)
            [[ $# -ge 2 ]] || die "$1 requires a value"
            docker_dir="$2"
            shift 2
            ;;
          --dockerfile-url)
            [[ $# -ge 2 ]] || die "$1 requires a value"
            dockerfile_url="$2"
            shift 2
            ;;
          *)
            die "Unknown option for enable: $1"
            ;;
        esac
      done
      build_image "$image" "$docker_dir" "$dockerfile_url"
      ;;
    run)
      run_conversion "$@"
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      die "Unknown command: $command"
      ;;
  esac
}

main "$@"
