import sys

from skills.paper_research_workflow_imports import SCRIPTS_DIR


if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mineru_cloud import (  # noqa: E402
    MinerUConfig,
    MinerUConfigError,
    load_mineru_config,
    resolve_standard_token,
    save_mineru_config,
)

import mineru_cloud  # noqa: E402


def test_save_and_load_mineru_token_config(tmp_path):
    config_path = tmp_path / ".paper-mineru.json"
    saved = save_mineru_config("secret-token", config_path)

    assert saved == MinerUConfig(standard_token="secret-token")
    assert load_mineru_config(config_path) == saved
    assert "secret-token" in config_path.read_text(encoding="utf-8")


def test_resolve_standard_token_prefers_environment(monkeypatch, tmp_path):
    config_path = tmp_path / ".paper-mineru.json"
    save_mineru_config("saved-token", config_path)
    monkeypatch.setenv("MINERU_TOKEN", "env-token")

    assert resolve_standard_token(config_path) == "env-token"


def test_resolve_standard_token_uses_saved_config(monkeypatch, tmp_path):
    config_path = tmp_path / ".paper-mineru.json"
    save_mineru_config("saved-token", config_path)
    monkeypatch.delenv("MINERU_TOKEN", raising=False)

    assert resolve_standard_token(config_path) == "saved-token"


def test_resolve_standard_token_reports_configuration_command(monkeypatch, tmp_path):
    config_path = tmp_path / ".paper-mineru.json"
    monkeypatch.delenv("MINERU_TOKEN", raising=False)

    try:
        resolve_standard_token(config_path)
    except MinerUConfigError as exc:
        message = str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected missing token to raise")

    assert "configure-mineru" in message
    assert "--standard-token" in message


def test_standard_cloud_uses_batch_upload_flow(monkeypatch, tmp_path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF")
    output = tmp_path / "mineru-out"
    calls = []

    def fake_json_request(method, url, payload=None, token=None, timeout=60):
        calls.append((method, url, payload, token))
        if url.endswith("/api/v4/file-urls/batch"):
            return {
                "data": {
                    "batch_id": "batch-1",
                    "file_urls": [{"upload_url": "https://upload.example/paper.pdf"}],
                }
            }
        if url.endswith("/api/v4/extract-results/batch/batch-1"):
            return {
                "data": {
                    "batch_id": "batch-1",
                    "extract_result": [{"state": "done", "full_zip_url": "https://download.example/result.zip"}],
                }
            }
        raise AssertionError(f"unexpected API call: {method} {url}")

    monkeypatch.setattr(mineru_cloud, "_json_request", fake_json_request)
    monkeypatch.setattr(mineru_cloud, "_put_file", lambda url, path: calls.append(("PUT", url, path.name, None)))
    monkeypatch.setattr(mineru_cloud, "_download", lambda url, path: calls.append(("DOWNLOAD", url, path.name, None)))
    monkeypatch.setattr(mineru_cloud, "_extract_zip", lambda zip_path, output_dir: calls.append(("UNZIP", str(zip_path), str(output_dir), None)))

    mineru_cloud.parse_with_standard_cloud(pdf, output, token="token", poll_interval=0)

    assert calls[0][1].endswith("/api/v4/file-urls/batch")
    assert calls[0][2]["files"] == [{"name": "paper.pdf", "data_id": "paper"}]
    assert calls[0][2]["model_version"] == "vlm"
    assert any(call[1].endswith("/api/v4/extract-results/batch/batch-1") for call in calls)
    assert not any("/api/v4/extract/task" in call[1] for call in calls if isinstance(call[1], str))


def test_standard_cloud_accepts_string_upload_urls(monkeypatch, tmp_path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF")
    output = tmp_path / "mineru-out"
    calls = []

    def fake_json_request(method, url, payload=None, token=None, timeout=60):
        calls.append((method, url, payload, token))
        if url.endswith("/api/v4/file-urls/batch"):
            return {
                "data": {
                    "batch_id": "batch-1",
                    "file_urls": ["https://upload.example/paper.pdf"],
                }
            }
        if url.endswith("/api/v4/extract-results/batch/batch-1"):
            return {
                "data": {
                    "batch_id": "batch-1",
                    "extract_result": [{"state": "done", "full_zip_url": "https://download.example/result.zip"}],
                }
            }
        raise AssertionError(f"unexpected API call: {method} {url}")

    monkeypatch.setattr(mineru_cloud, "_json_request", fake_json_request)
    monkeypatch.setattr(mineru_cloud, "_put_file", lambda url, path: calls.append(("PUT", url, path.name, None)))
    monkeypatch.setattr(mineru_cloud, "_download", lambda url, path: calls.append(("DOWNLOAD", url, path.name, None)))
    monkeypatch.setattr(mineru_cloud, "_extract_zip", lambda zip_path, output_dir: calls.append(("UNZIP", str(zip_path), str(output_dir), None)))

    mineru_cloud.parse_with_standard_cloud(pdf, output, token="token", poll_interval=0)

    assert ("PUT", "https://upload.example/paper.pdf", "paper.pdf", None) in calls


def test_cloud_requests_ignore_system_proxy_by_default(monkeypatch):
    opener_handlers = []

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b"{}"

    class FakeOpener:
        def open(self, request, timeout=60):
            return FakeResponse()

    def fake_build_opener(*handlers):
        opener_handlers.extend(handlers)
        return FakeOpener()

    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    monkeypatch.delenv("MINERU_USE_PROXY", raising=False)
    monkeypatch.setattr(mineru_cloud.urllib.request, "build_opener", fake_build_opener)

    mineru_cloud._json_request("GET", "https://mineru.net/api/test")

    assert opener_handlers
    assert isinstance(opener_handlers[0], mineru_cloud.urllib.request.ProxyHandler)
    assert opener_handlers[0].proxies == {}


def test_cloud_requests_can_opt_into_system_proxy(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b"{}"

    opened = []

    def fake_urlopen(request, timeout=60):
        opened.append((request, timeout))
        return FakeResponse()

    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("MINERU_USE_PROXY", "1")
    monkeypatch.setattr(mineru_cloud.urllib.request, "urlopen", fake_urlopen)

    mineru_cloud._json_request("GET", "https://mineru.net/api/test")

    assert opened


def test_presigned_upload_does_not_add_content_type_header(monkeypatch, tmp_path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF")
    captured = []

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b""

    def fake_open_url(request, timeout=300):
        captured.append(request)
        return FakeResponse()

    monkeypatch.setattr(mineru_cloud, "_open_url", fake_open_url)

    mineru_cloud._put_file("https://oss.example/paper.pdf?signature=abc", pdf)

    assert captured
    assert captured[0].get_method() == "PUT"
    assert captured[0].get_header("Content-type") is None
    assert captured[0].get_header("Content-Type") is None
