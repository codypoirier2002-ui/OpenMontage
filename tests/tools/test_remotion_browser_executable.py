from tools.video.video_compose import _remotion_browser_args


def test_no_browser_flag_when_env_unset(monkeypatch) -> None:
    monkeypatch.delenv("REMOTION_BROWSER_EXECUTABLE", raising=False)

    assert _remotion_browser_args() == []


def test_browser_flag_from_env(monkeypatch) -> None:
    monkeypatch.setenv("REMOTION_BROWSER_EXECUTABLE", "/opt/chromium/headless_shell")

    assert _remotion_browser_args() == ["--browser-executable=/opt/chromium/headless_shell"]
