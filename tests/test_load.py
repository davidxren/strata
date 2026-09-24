import struct
from pathlib import Path

import pytest

from bench.load import (
    HEADER,
    SAMPLE_GAPS,
    SAMPLE_ROWS,
    VALUE_COLUMNS,
    read_csv,
    sample_columns,
    write_csv,
)
from bench.synthetic import STEP_MS, Dataset

SAMPLE = Path(__file__).parent / "data" / "sample.csv"


def packed(values: list[float]) -> list[bytes]:
    return [struct.pack("<d", v) for v in values]


def test_sample_file_is_the_generator_output(tmp_path: Path) -> None:
    regenerated = tmp_path / "sample.csv"
    write_csv(regenerated, sample_columns())
    assert regenerated.read_bytes() == SAMPLE.read_bytes()


def test_one_series_per_value_column_in_header_order() -> None:
    series = read_csv(SAMPLE)
    assert [s.name for s in series] == list(VALUE_COLUMNS)
    assert len(series) == 4


def test_empty_cells_are_skipped() -> None:
    for s in read_csv(SAMPLE):
        gap = SAMPLE_GAPS.get(s.name, 0)
        blanks = len(range(0, SAMPLE_ROWS, gap)) if gap else 0
        assert len(s.ts_ms) == len(s.values) == SAMPLE_ROWS - blanks
        assert s.ts_ms == sorted(set(s.ts_ms))
        if gap:
            assert all((t // STEP_MS) % gap for t in s.ts_ms)


def test_loaded_values_match_the_generator_bit_for_bit() -> None:
    for loaded, generated in zip(read_csv(SAMPLE), sample_columns(), strict=True):
        assert loaded.ts_ms == generated.ts_ms
        assert packed(loaded.values) == packed(generated.values)


def test_write_then_read_round_trips(tmp_path: Path) -> None:
    columns = sample_columns(50)
    path = tmp_path / "small.csv"
    write_csv(path, columns)
    assert read_csv(path) == columns


def test_wrong_header_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("ts_ms,heart_rate\n0,1\n")
    with pytest.raises(ValueError):
        read_csv(path)


def test_empty_file_raises(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("")
    with pytest.raises(ValueError):
        read_csv(path)


def test_short_row_raises(tmp_path: Path) -> None:
    path = tmp_path / "ragged.csv"
    path.write_text(",".join(HEADER) + "\n0,1,2,3\n")
    with pytest.raises(ValueError):
        read_csv(path)


def test_write_csv_rejects_other_columns(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        write_csv(tmp_path / "x.csv", [Dataset("x", [0], [1.0])])
