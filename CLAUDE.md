# CLAUDE.md — Oldcircle/claude-tap (fork)

This file is the entry point for AI agents working in this repo.

## Project Overview

Fork of [`liaohch3/claude-tap`](https://github.com/liaohch3/claude-tap) that
adds a `dscode` client to `--tap-client`, so our `dscode` CLI (from
[Oldcircle/deepseek-code](https://github.com/Oldcircle/deepseek-code)) can be
traced.

Upstream's rules and engineering policies still apply — see `AGENTS.md`
(which routes to `.agents/docs/standards/*.md`). The fork only adds
DeepSeek-specific glue; do not rewrite or relax upstream policies.

## Active docs

| File | Purpose |
|------|---------|
| [FORK.md](./FORK.md) | Fork rationale, remote topology, upstream sync strategy |
| [AGENTS.md](./AGENTS.md) | **Upstream maintainer rules — authoritative for code style, gates, commit etiquette** |
| [docs/support-matrix.md](./docs/support-matrix.md) | Verified client × auth × target × transport combinations (now includes dscode rows) |

## Commands

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Lint + format + tests (the mandatory pre-commit gate)
uv run ruff check .
uv run ruff format --check .
uv run pytest tests/ -x --timeout=60

# Run the dscode-specific tests in isolation
uv run pytest tests/test_dscode_launch.py -v

# Live use against our local dscode
echo "hi" | claude-tap --tap-client dscode --tap-no-open -- -p
```

## Where the dscode wiring lives

- `claude_tap/cli.py` — `CLIENT_CONFIGS["dscode"]` definition + help epilog example
- `tests/test_dscode_launch.py` — unit coverage
- `docs/support-matrix.md` — two rows under "Client Configurations" + a row
  under "Default Proxy Mode by Client"

Keep changes additive. Cherry-pick upstream commits rather than rebasing
to avoid conflicts in `CLIENT_CONFIGS`.
