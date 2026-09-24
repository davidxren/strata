import sqlite3
import struct
import tempfile
from pathlib import Path

import pytest

from bench.baselines import (
    NAMES,
    RAW_BYTES_PER_SAMPLE,
    baselines,
    gzip_bytes_per_sample,
    parquet_bytes_per_sample,
    raw_bytes,
    raw_bytes_per_sample,
    sqlite_bytes_per_sample,
    write_parquet,
    write_sqlite,
)
from bench.synthetic import constants, random_bits, slow_integers

N = 1000


def test_raw_is_sixteen_bytes_per_sample() -> None:
    data = slow_integers(N)
    assert raw_bytes_per_sample(data.ts_ms, data.values) == RAW_BYTES_PER_SAMPLE


def test_raw_bytes_are_little_endian_pairs_in_order() -> None:
    assert raw_bytes([0, 1000], [1.5, -0.0]) == struct.pack("<qdqd", 0, 1.5, 1000, -0.0)


def test_mismatched_or_empty_input_raises() -> None:
    with pytest.raises(ValueError):
        raw_bytes([0], [])
    with pytest.raises(ValueError):
        raw_bytes([], [])


def test_gzip_shrinks_constants_and_not_random_bits() -> None:
    flat = constants(N)
    noise = random_bits(N)
    assert gzip_bytes_per_sample(flat.ts_ms, flat.values) < RAW_BYTES_PER_SAMPLE / 2
    assert gzip_bytes_per_sample(noise.ts_ms, noise.values) > RAW_BYTES_PER_SAMPLE / 2


def test_gzip_is_deterministic() -> None:
    data = slow_integers(N)
    first = gzip_bytes_per_sample(data.ts_ms, data.values)
    assert first == gzip_bytes_per_sample(data.ts_ms, data.values)


def test_sqlite_table_index_and_rows(tmp_path: Path) -> None:
    data = slow_integers(N)
    path = tmp_path / "samples.db"
    write_sqlite(path, 3, data.ts_ms, data.values)
    conn = sqlite3.connect(path)
    columns = [row[1] for row in conn.execute("PRAGMA table_info(samples)")]
    assert columns == ["series_id", "ts", "value"]
    (index_sql,) = conn.execute("SELECT sql FROM sqlite_master WHERE type = 'index'").fetchone()
    assert index_sql.endswith("ON samples (series_id, ts)")
    rows = conn.execute("SELECT series_id, ts, value FROM samples ORDER BY ts").fetchall()
    conn.close()
    assert rows == [(3, t, v) for t, v in zip(data.ts_ms, data.values, strict=True)]


def test_sqlite_size_is_measured_and_cleaned_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    data = slow_integers(N)
    assert sqlite_bytes_per_sample(data.ts_ms, data.values) > RAW_BYTES_PER_SAMPLE
    assert list(tmp_path.iterdir()) == []


def test_parquet_round_trips_with_zstd(tmp_path: Path) -> None:
    pq = pytest.importorskip("pyarrow.parquet")
    data = slow_integers(N)
    path = tmp_path / "samples.parquet"
    write_parquet(path, data.ts_ms, data.values)
    table = pq.read_table(path)
    assert table.column("ts_ms").to_pylist() == data.ts_ms
    assert table.column("value").to_pylist() == data.values
    assert pq.ParquetFile(path).metadata.row_group(0).column(1).compression == "ZSTD"
    assert parquet_bytes_per_sample(data.ts_ms, data.values) < RAW_BYTES_PER_SAMPLE


def test_baselines_returns_every_name_in_order() -> None:
    pytest.importorskip("pyarrow")
    data = constants(N)
    result = baselines(data.ts_ms, data.values)
    assert tuple(result) == NAMES
    assert result["raw"] == RAW_BYTES_PER_SAMPLE
    assert all(v > 0 for v in result.values())


def test_baselines_measure_sqlite_under_the_given_series_id() -> None:
    pytest.importorskip("pyarrow")
    data = slow_integers(N)
    expected = sqlite_bytes_per_sample(data.ts_ms, data.values, 3)
    assert baselines(data.ts_ms, data.values, 3)["sqlite"] == expected
