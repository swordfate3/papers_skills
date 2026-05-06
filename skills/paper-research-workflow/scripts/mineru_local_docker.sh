#!/usr/bin/env bash
set -euo pipefail

DEFAULT_IMAGE="${MINERU_IMAGE:-mineru:latest}"
DEFAULT_DOCKER_DIR="${MINERU_DOCKER_DIR:-$HOME/docker_files/mineru}"
DEFAULT_DOCKERFILE_URL="${MINERU_DOCKERFILE_URL:-https://raw.githubusercontent.com/opendatalab/MinerU/master/docker/global/Dockerfile}"
DEFAULT_SOURCE_ARCHIVE_URL="${MINERU_SOURCE_ARCHIVE_URL:-https://github.com/opendatalab/MinerU/archive/refs/heads/master.tar.gz}"
DEFAULT_SOURCE_SUBDIR="${MINERU_SOURCE_SUBDIR:-docker/global}"

usage() {
  cat <<'USAGE'
Usage:
  mineru_local_docker.sh <command> [options]

Commands:
  status
      Show whether docker exists and whether the MinerU image is ready.

  enable [--image IMAGE] [--docker-dir DIR]
      Build the MinerU Docker image locally.
      If DIR is missing, the script can prepare a full build context from
      --source-archive-url and --source-subdir, or fall back to --dockerfile-url.

  run [options] <input-file-or-directory>
      Convert a local file with the built MinerU Docker image.

Run options:
  -o, --output DIR
  --image IMAGE
  --docker-dir DIR
  --dockerfile-url URL
  --source-archive-url URL
  --source-subdir PATH
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

copy_dir_contents() {
  local source_dir="$1"
  local target_dir="$2"

  mkdir -p "$target_dir"
  cp -R "$source_dir"/. "$target_dir"/
}

extract_archive() {
  local archive_path="$1"
  local output_dir="$2"

  mkdir -p "$output_dir"
  case "$archive_path" in
    *.tar.gz|*.tgz)
      tar -xzf "$archive_path" -C "$output_dir"
      ;;
    *.zip)
      command -v unzip >/dev/null 2>&1 || die "unzip command not found"
      unzip -q "$archive_path" -d "$output_dir"
      ;;
    *)
      die "Unsupported source archive format: $archive_path"
      ;;
  esac
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
  local source_archive_url="$4"
  local source_subdir="$5"

  command -v docker >/dev/null 2>&1 || die "docker command not found"
  docker info >/dev/null 2>&1 || die "docker daemon is not running"

  if [[ ! -f "$docker_dir/Dockerfile" ]]; then
    mkdir -p "$docker_dir"
    command -v curl >/dev/null 2>&1 || die "curl command not found"

    if [[ -n "$source_archive_url" ]]; then
      local tmp_dir
      tmp_dir="$(mktemp -d)"
      trap 'rm -rf "$tmp_dir"' RETURN

      local archive_ext=".tar.gz"
      [[ "$source_archive_url" == *.zip ]] && archive_ext=".zip"

      local archive_path="$tmp_dir/source$archive_ext"
      local extracted_dir="$tmp_dir/extracted"

      curl -fsSL "$source_archive_url" -o "$archive_path"
      extract_archive "$archive_path" "$extracted_dir"

      local root_dir
      root_dir="$(find "$extracted_dir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
      [[ -n "$root_dir" ]] || die "No root directory found in source archive: $source_archive_url"

      local source_dir="$root_dir"
      if [[ -n "$source_subdir" ]]; then
        source_dir="$root_dir/$source_subdir"
      fi
      [[ -d "$source_dir" ]] || die "Source subdir not found in archive: $source_subdir"

      copy_dir_contents "$source_dir" "$docker_dir"
      trap - RETURN
      rm -rf "$tmp_dir"
    fi

    if [[ ! -f "$docker_dir/Dockerfile" ]]; then
      curl -fsSL "$dockerfile_url" -o "$docker_dir/Dockerfile"
    fi
  fi

  docker build -t "$image" "$docker_dir"
}

run_conversion() {
  local image="$DEFAULT_IMAGE"
  local docker_dir="$DEFAULT_DOCKER_DIR"
  local dockerfile_url="$DEFAULT_DOCKERFILE_URL"
  local source_archive_url="$DEFAULT_SOURCE_ARCHIVE_URL"
  local source_subdir="$DEFAULT_SOURCE_SUBDIR"
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
      --source-archive-url)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        source_archive_url="$2"
        shift 2
        ;;
      --source-subdir)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        source_subdir="$2"
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
    build_image "$image" "$docker_dir" "$dockerfile_url" "$source_archive_url" "$source_subdir"
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
      local source_archive_url="$DEFAULT_SOURCE_ARCHIVE_URL"
      local source_subdir="$DEFAULT_SOURCE_SUBDIR"
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
          --source-archive-url)
            [[ $# -ge 2 ]] || die "$1 requires a value"
            source_archive_url="$2"
            shift 2
            ;;
          --source-subdir)
            [[ $# -ge 2 ]] || die "$1 requires a value"
            source_subdir="$2"
            shift 2
            ;;
          *)
            die "Unknown option for enable: $1"
            ;;
        esac
      done
      build_image "$image" "$docker_dir" "$dockerfile_url" "$source_archive_url" "$source_subdir"
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
