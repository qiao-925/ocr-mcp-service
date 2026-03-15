"""Tests for the simplified CLI entrypoint."""

from __future__ import annotations

import pytest

from local_ocr_mcp import __main__ as main_module


def test_main_uses_stdio_by_default(monkeypatch) -> None:
    """Main should start the server with stdio by default."""
    captured: dict[str, str] = {}
    logger = type("Logger", (), {"info": lambda *args, **kwargs: None})()
    fake_mcp = type("FakeMCP", (), {"run": lambda self, **kwargs: captured.update(kwargs)})()

    monkeypatch.setattr(main_module.sys, "argv", ["local-ocr-mcp"])
    monkeypatch.setattr(main_module, "get_logger", lambda name: logger)
    monkeypatch.setattr(main_module, "mcp", fake_mcp)

    main_module.main()

    assert captured == {"transport": "stdio"}


def test_main_rejects_removed_transport_flag(monkeypatch) -> None:
    """Main should reject the removed transport flag entirely."""
    monkeypatch.setattr(main_module, "get_logger", lambda name: object())
    monkeypatch.setattr(
        main_module.sys,
        "argv",
        ["local-ocr-mcp", "--transport", "stdio"],
    )

    with pytest.raises(SystemExit) as exc_info:
        main_module.main()

    assert exc_info.value.code == 2


def test_main_treats_cancelled_shutdown_as_clean_exit(monkeypatch) -> None:
    """Cancelled shutdowns should map to a zero exit code."""
    logger = type("Logger", (), {"info": lambda *args, **kwargs: None})()
    fake_mcp = type(
        "FakeMCP",
        (),
        {
            "run": lambda self, **kwargs: (_ for _ in ()).throw(
                main_module.asyncio.CancelledError()
            )
        },
    )()

    monkeypatch.setattr(main_module.sys, "argv", ["local-ocr-mcp"])
    monkeypatch.setattr(main_module, "get_logger", lambda name: logger)
    monkeypatch.setattr(main_module, "mcp", fake_mcp)

    with pytest.raises(SystemExit) as exc_info:
        main_module.main()

    assert exc_info.value.code == 0
