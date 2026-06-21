"""ValueRacer CLI wrapper for the legacy orchestrator implementation."""

from __future__ import annotations

from elementkonfluenz_orchestrator.cli import build_parser, main

__all__ = ["build_parser", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
