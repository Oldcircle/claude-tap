# FORK.md — Oldcircle/claude-tap

This is a fork of [`liaohch3/claude-tap`](https://github.com/liaohch3/claude-tap)
maintained at [`Oldcircle/claude-tap`](https://github.com/Oldcircle/claude-tap).

## Why we forked

To add a `dscode` client to `--tap-client`, so that
[Oldcircle/deepseek-code](https://github.com/Oldcircle/deepseek-code) (our
DeepSeek-focused Claude Code fork, installed as the `dscode` command) can be
traced by claude-tap.

Upstream's reverse-proxy flow patches `ANTHROPIC_BASE_URL`. Our `dscode`
reads the dedicated `DEEPSEEK_BASE_URL`, so upstream's `--tap-client claude`
would not redirect dscode traffic.

## Local remotes

| Remote | URL | Purpose |
|--------|-----|---------|
| `origin` | `git@github.com:Oldcircle/claude-tap.git` | Day-to-day push/pull |
| `upstream` | `https://github.com/liaohch3/claude-tap.git` | Track upstream changes; cherry-pick selectively |

## What we changed

- `claude_tap/cli.py`
  - Added `dscode` entry to `CLIENT_CONFIGS` (`base_url_env=DEEPSEEK_BASE_URL`,
    `base_url_suffix=/v1`, default target `https://api.deepseek.com`)
  - Mirrors the codex pattern for path normalization (keep `/v1` when target
    is `api.deepseek.com`, strip otherwise)
  - Added a usage example block to the help epilog
- `tests/test_dscode_launch.py` — 3 unit tests (reverse / forward / config sanity)
- `docs/support-matrix.md` — appended dscode rows + default-mode entry

## Usage

```bash
# Default — forward to api.deepseek.com via OpenAI-compatible /v1/* paths
claude-tap --tap-client dscode

# Real-time browser viewer
claude-tap --tap-client dscode --tap-live

# Self-hosted DeepSeek (e.g. vLLM on port 8000 without /v1 base path)
claude-tap --tap-client dscode --tap-target http://localhost:8000

# Pipe mode
echo "hi" | claude-tap --tap-client dscode --tap-no-open -- -p
```

`DEEPSEEK_API_KEY` must be set in env. dscode reads it directly (claude-tap
does not touch credentials).

## Upstream sync strategy

- No periodic rebase. Cherry-pick specific upstream commits when needed.
- Keep our diff scoped to:
  - `claude_tap/cli.py` `CLIENT_CONFIGS` and epilog (additive only)
  - `tests/test_dscode_launch.py` (new file)
  - `docs/support-matrix.md` (additive rows)
- If upstream adopts `dscode` natively (via PR), delete `FORK.md` and drop
  the fork-specific copies.
