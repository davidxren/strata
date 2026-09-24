import shutil
from collections.abc import Sequence
from pathlib import Path

import pytest

from bench.baselines import NAMES
from bench.load import VALUE_COLUMNS
from bench.run import (
    NOTE,
    STRATA_COLUMN,
    Row,
    Table,
    platform_line,
    real_tables,
    render,
    report,
    run,
    synthetic_table,
)
from bench.synthetic import all_datasets

SAMPLE = Path(__file__).parent / "data" / "sample.csv"
N = 200


@pytest.fixture(autouse=True)
def pyarrow() -> None:
    pytest.importorskip("pyarrow")


def test_synthetic_table_has_a_row_per_generator() -> None:
    table = synthetic_table(N)
    assert table.label == "synthetic"
    assert [r.name for r in table.rows] == [d.name for d in all_datasets(1)]
    assert all(r.samples == N and tuple(r.bytes_per_sample) == NAMES for r in table.rows)


def test_report_without_real_data_is_synthetic_only(tmp_path: Path) -> None:
    text = report(N, tmp_path / "missing")
    assert text.count("## ") == 1
    assert text.startswith("## synthetic\n")
    assert "## real" not in text
    assert NOTE in text
    assert text.count(STRATA_COLUMN) == len(all_datasets(1))
    assert text.endswith(platform_line() + "\n")


def test_report_labels_csv_files_real(tmp_path: Path) -> None:
    shutil.copy(SAMPLE, tmp_path / "run.csv")
    text = report(N, tmp_path)
    assert text.index("## synthetic") < text.index("## real: run.csv")
    for name in VALUE_COLUMNS:
        assert f"| {name} |" in text


def test_render_formats_two_decimals() -> None:
    row = Row("x", 3, {"raw": 16.0, "gzip": 1.234, "sqlite": 40.0, "parquet": 2.005})
    text = render([Table("synthetic", [row])])
    assert "| x | 3 | 16.00 | 1.23 | 40.00 | 2.00 | not implemented |" in text


def test_run_prints_and_writes_the_same_text(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "bench.md"
    text = run(N, tmp_path / "missing", out)
    assert out.read_text() == text == capsys.readouterr().out


def test_run_without_out_only_prints(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(N, tmp_path / "missing", None)
    assert capsys.readouterr().out.startswith("## synthetic\n")
    assert list(tmp_path.iterdir()) == []


def test_real_rows_are_measured_under_their_column_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def recorded(
        ts_ms: Sequence[int], values: Sequence[float], series_id: int = 0
    ) -> dict[str, float]:
        return dict.fromkeys(NAMES, float(series_id))

    monkeypatch.setattr("bench.run.baselines", recorded)
    shutil.copy(SAMPLE, tmp_path / "run.csv")
    synthetic = synthetic_table(N)
    (real,) = real_tables(tmp_path)
    assert [r.bytes_per_sample["sqlite"] for r in synthetic.rows] == [0.0] * len(synthetic.rows)
    assert [r.bytes_per_sample["sqlite"] for r in real.rows] == [0.0, 1.0, 2.0, 3.0]
