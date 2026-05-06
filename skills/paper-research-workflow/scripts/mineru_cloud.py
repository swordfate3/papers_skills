from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from shared.scripts.paper_research_common import read_json, write_json
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    from paper_research_common import read_json, write_json


DEFAULT_MINERU_CONFIG = ".paper-mineru.json"
MINERU_API_BASE = "https://mineru.net"


class MinerUConfigError(RuntimeError):
    pass


class MinerUApiError(RuntimeError):
    pass


@dataclass(frozen=True)
class MinerUConfig:
    standard_token: str = ""


def default_config_path() -> Path:
    return Path(__file__).resolve().parents[1] / DEFAULT_MINERU_CONFIG


def save_mineru_config(standard_token: str, config_path: Path | None = None) -> MinerUConfig:
    token = standard_token.strip()
    config = MinerUConfig(standard_token=token)
    write_json(config_path or default_config_path(), {"standard_token": token})
    return config


def load_mineru_config(config_path: Path | None = None) -> MinerUConfig:
    path = config_path or default_config_path()
    if not path.exists():
        return MinerUConfig()
    data = read_json(path)
    if not isinstance(data, dict):
        return MinerUConfig()
    return MinerUConfig(standard_token=str(data.get("standard_token") or "").strip())


def mineru_config_status(config_path: Path | None = None) -> dict[str, Any]:
    config = load_mineru_config(config_path)
    return {
        "config_path": str((config_path or default_config_path()).resolve()),
        "standard_token_configured": bool(config.standard_token),
        "env_token_configured": bool(os.environ.get("MINERU_TOKEN", "").strip()),
    }


def resolve_standard_token(config_path: Path | None = None) -> str:
    env_token = os.environ.get("MINERU_TOKEN", "").strip()
    if env_token:
        return env_token
    saved_token = load_mineru_config(config_path).standard_token
    if saved_token:
        return saved_token
    raise MinerUConfigError(
        "MinerU high-quality mode requires a token. Run: "
        "python scripts/paper_workflow.py configure-mineru --standard-token <token>"
    )


def _json_request(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with _open_url(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:  # pragma: no cover - network path
        detail = exc.read().decode("utf-8", errors="replace")
        raise MinerUApiError(f"MinerU API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network path
        raise MinerUApiError(f"MinerU API request failed: {exc}") from exc
    return json.loads(body or "{}")


def _put_file(url: str, path: Path, timeout: int = 300) -> None:
    data = path.read_bytes()
    request = urllib.request.Request(url, data=data, method="PUT")
    try:
        with _open_url(request, timeout=timeout) as response:
            response.read()
    except urllib.error.HTTPError as exc:  # pragma: no cover - network path
        detail = exc.read().decode("utf-8", errors="replace")
        if "SignatureDoesNotMatch" in detail:
            detail = (
                "OSS presigned upload signature mismatch. The request was sent without extra Content-Type headers; "
                f"server detail: {detail}"
            )
        raise MinerUApiError(f"MinerU upload HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network path
        raise MinerUApiError(f"MinerU upload failed: {exc}") from exc


def _download(url: str, output: Path, timeout: int = 300) -> None:
    try:
        with _open_url(url, timeout=timeout) as response:
            output.write_bytes(response.read())
    except urllib.error.HTTPError as exc:  # pragma: no cover - network path
        detail = exc.read().decode("utf-8", errors="replace")
        raise MinerUApiError(f"MinerU download HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network path
        raise MinerUApiError(f"MinerU download failed: {exc}") from exc


def _use_system_proxy() -> bool:
    return os.environ.get("MINERU_USE_PROXY", "").strip().lower() in {"1", "true", "yes", "on"}


def _open_url(request: urllib.request.Request | str, timeout: int):
    if _use_system_proxy():
        return urllib.request.urlopen(request, timeout=timeout)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return opener.open(request, timeout=timeout)


def _extract_zip(zip_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(output_dir)


def _first_value(data: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = data.get(key)
        if value:
            return value
    return None


def _poll_task(task_url: str, token: str | None, timeout_seconds: int, poll_interval: int) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        last = _json_request("GET", task_url, token=token)
        status = str(last.get("status") or last.get("state") or "").lower()
        if status in {"done", "success", "completed", "finish", "finished"}:
            return last
        if status in {"failed", "error", "fail"}:
            raise MinerUApiError(f"MinerU task failed: {last}")
        time.sleep(poll_interval)
    raise MinerUApiError(f"MinerU task timed out: {last}")


def _extract_batch_item(result: dict[str, Any]) -> dict[str, Any]:
    data = result.get("data") or result
    items = data.get("extract_result") or data.get("extract_results") or data.get("results") or []
    if isinstance(items, list) and items:
        return items[0]
    if isinstance(items, dict):
        return items
    return data


def _poll_batch(batch_id: str, token: str, timeout_seconds: int, poll_interval: int, api_base: str) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last: dict[str, Any] = {}
    url = f"{api_base}/api/v4/extract-results/batch/{urllib.parse.quote(str(batch_id))}"
    while time.monotonic() < deadline:
        last = _json_request("GET", url, token=token)
        item = _extract_batch_item(last)
        state = str(item.get("state") or item.get("status") or "").lower()
        if state in {"done", "success", "completed", "finish", "finished"}:
            return last
        if state in {"failed", "error", "fail"}:
            raise MinerUApiError(f"MinerU batch task failed: {last}")
        time.sleep(poll_interval)
    raise MinerUApiError(f"MinerU batch task timed out: {last}")


def parse_with_standard_cloud(
    pdf_path: Path,
    output_dir: Path,
    token: str | None = None,
    config_path: Path | None = None,
    timeout_seconds: int = 1800,
    poll_interval: int = 5,
    api_base: str = MINERU_API_BASE,
) -> dict[str, Any]:
    resolved_token = token or resolve_standard_token(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    upload_info = _json_request(
        "POST",
        f"{api_base}/api/v4/file-urls/batch",
        {
            "files": [{"name": pdf_path.name}],
            "enable_formula": True,
            "enable_table": True,
            "language": "auto",
        },
        token=resolved_token,
    )
    upload_data = upload_info.get("data") or upload_info
    batch_id = upload_data.get("batch_id")
    upload_items = upload_data.get("file_urls") or upload_data.get("files") or upload_info.get("file_urls")
    if not upload_items:
        raise MinerUApiError(f"MinerU upload URL response missing files: {upload_info}")
    first = upload_items[0] if isinstance(upload_items, list) else next(iter(upload_items.values()))
    upload_url = _first_value(first, ["upload_url", "url", "file_url"]) if isinstance(first, dict) else str(first)
    if not upload_url:
        raise MinerUApiError(f"MinerU upload URL missing: {upload_info}")
    if not batch_id:
        raise MinerUApiError(f"MinerU batch response missing batch_id: {upload_info}")

    _put_file(str(upload_url), pdf_path)
    result = _poll_batch(
        str(batch_id),
        token=resolved_token,
        timeout_seconds=timeout_seconds,
        poll_interval=poll_interval,
        api_base=api_base,
    )
    result_data = _extract_batch_item(result)
    zip_url = _first_value(result_data, ["full_zip_url", "zip_url", "result_zip", "result_url"])
    markdown_url = _first_value(result_data, ["markdown_url", "md_url"])
    if zip_url:
        zip_path = output_dir / "mineru-result.zip"
        _download(str(zip_url), zip_path)
        _extract_zip(zip_path, output_dir)
    elif markdown_url:
        _download(str(markdown_url), output_dir / "full.md")
    else:
        raise MinerUApiError(f"MinerU result missing downloadable artifact: {result}")
    return result


def parse_with_agent_cloud(
    pdf_path: Path,
    output_dir: Path,
    timeout_seconds: int = 900,
    poll_interval: int = 5,
    api_base: str = MINERU_API_BASE,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    task = _json_request("POST", f"{api_base}/api/v1/agent/parse/file", {"filename": pdf_path.name})
    task_id = task.get("task_id") or task.get("data", {}).get("task_id")
    upload_url = task.get("file_url") or task.get("data", {}).get("file_url")
    if not task_id or not upload_url:
        raise MinerUApiError(f"MinerU agent parse response missing task_id/file_url: {task}")

    _put_file(str(upload_url), pdf_path)
    result = _poll_task(
        f"{api_base}/api/v1/agent/parse/{urllib.parse.quote(str(task_id))}",
        token=None,
        timeout_seconds=timeout_seconds,
        poll_interval=poll_interval,
    )
    result_data = result.get("result") or result.get("data") or result
    markdown_url = _first_value(result_data, ["markdown_url", "md_url", "url"])
    if not markdown_url:
        raise MinerUApiError(f"MinerU agent result missing markdown_url: {result}")
    _download(str(markdown_url), output_dir / "full.md")
    return result
