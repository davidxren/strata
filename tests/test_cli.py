import subprocess
import sys
from importlib.metadata import entry_points
from pathlib import Path

import pytest

from strata.cli import main


def test_importing_the_cli_loads_nothing_outside_the_stdlib() -> None:
    code = (
        "import sys; before = set(sys.modules); import strata.cli;"
        "allowed = sys.stdlib_module_names | {'strata'};"
        "print(sorted(m for m in set(sys.modules) - before if m.split('.')[0] not in allowed))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], check=True, capture_output=True, text=True
    )
    assert result.stdout.strip() == "[]"


def test_no_command_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exit_info:
        main([])
    assert exit_info.value.code == 2


def test_console_script_points_at_main() -> None:
    (script,) = entry_points(group="console_scripts", name="strata")
    assert script.value == "strata.cli:main"


def test_bench_writes_the_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pytest.importorskip("pyarrow")
    out = tmp_path / "bench.md"
    argv = ["bench", "--samples", "50", "--data", str(tmp_path / "missing"), "--out", str(out)]
    assert main(argv) == 0
    assert out.read_text() == capsys.readouterr().out
    assert out.read_text().startswith("## synthetic\n")
