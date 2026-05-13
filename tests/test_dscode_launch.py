from __future__ import annotations

import asyncio

import pytest

from claude_tap.cli import run_client


class _DummyProc:
    def __init__(self) -> None:
        self.pid = 12345
        self.returncode: int | None = None

    async def wait(self) -> int:
        self.returncode = 0
        return 0

    def terminate(self) -> None:
        self.returncode = 0

    def kill(self) -> None:
        self.returncode = -9


@pytest.mark.asyncio
async def test_run_client_dscode_reverse_injects_deepseek_base_url(monkeypatch) -> None:
    """Reverse mode must point dscode at the proxy via DEEPSEEK_BASE_URL."""
    captured: dict[str, object] = {}

    async def fake_create_subprocess_exec(*cmd, **kwargs):
        captured["cmd"] = cmd
        captured["env"] = kwargs["env"]
        return _DummyProc()

    monkeypatch.setattr("claude_tap.cli.shutil.which", lambda _: "/tmp/dscode")
    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    code = await run_client(43123, ["-p", "hello"], client="dscode", proxy_mode="reverse")

    assert code == 0
    assert captured["cmd"] == ("/tmp/dscode", "-p", "hello")
    # The /v1 suffix matches DeepSeek's OpenAI-compatible chat completions path.
    assert captured["env"]["DEEPSEEK_BASE_URL"] == "http://127.0.0.1:43123/v1"


@pytest.mark.asyncio
async def test_run_client_dscode_forward_sets_https_proxy(monkeypatch) -> None:
    """Forward mode should inject HTTPS_PROXY instead of touching DEEPSEEK_BASE_URL."""
    captured: dict[str, object] = {}

    async def fake_create_subprocess_exec(*cmd, **kwargs):
        captured["cmd"] = cmd
        captured["env"] = kwargs["env"]
        return _DummyProc()

    monkeypatch.setattr("claude_tap.cli.shutil.which", lambda _: "/tmp/dscode")
    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    code = await run_client(43200, ["-p", "hi"], client="dscode", proxy_mode="forward")

    assert code == 0
    assert captured["env"]["HTTPS_PROXY"] == "http://127.0.0.1:43200"
    assert captured["env"]["http_proxy"] == "http://127.0.0.1:43200"
    # DEEPSEEK_BASE_URL must not be set in forward mode (let the SDK reach the
    # upstream normally; the proxy intercepts at the network layer).
    assert (
        "DEEPSEEK_BASE_URL" not in captured["env"]
        or captured["env"].get("DEEPSEEK_BASE_URL") != "http://127.0.0.1:43200/v1"
    )


def test_dscode_default_target_is_deepseek_api() -> None:
    from claude_tap.cli import CLIENT_CONFIGS

    cfg = CLIENT_CONFIGS["dscode"]
    assert cfg.base_url_env == "DEEPSEEK_BASE_URL"
    assert cfg.base_url_suffix == "/v1"
    assert cfg.default_target == "https://api.deepseek.com"
    # /v1 prefix should be kept for the default api.deepseek.com target.
    assert cfg.reverse_strip_path_prefix("https://api.deepseek.com") == ""
    # And stripped for self-hosted endpoints that don't include /v1 in their path.
    assert cfg.reverse_strip_path_prefix("http://localhost:8000") == "/v1"
