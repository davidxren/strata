import gzip
import sqlite3
import struct
import tempfile
from collections.abc import Sequence
from pathlib import Path

RAW_BYTES_PER_SAMPLE = 16
GZIP_LEVEL = 6
NAMES = ("raw", "gzip", "sqlite", "parquet")

SAMPLE = struct.Struct("<qd")


def sample_count(ts_ms: Sequence[int], values: Sequence[float]) -> int:
    if len(ts_ms) != len(values):
        raise ValueError(f"{len(ts_ms)} timestamps for {len(values)} values")
    if not ts_ms:
        raise ValueError("no samples")
    return len(ts_ms)


def raw_bytes(ts_ms: Sequence[int], values: Sequence[float]) -> bytes:
    sample_count(ts_ms, values)
    return b"".join(map(SAMPLE.pack, ts_ms, values))


def raw_bytes_per_sample(ts_ms: Sequence[int], values: Sequence[float]) -> float:
    return len(raw_bytes(ts_ms, values)) / sample_count(ts_ms, values)


def gzip_bytes_per_sample(ts_ms: Sequence[int], values: Sequence[float]) -> float:
    packed = gzip.compress(raw_bytes(ts_ms, values), compresslevel=GZIP_LEVEL, mtime=0)
    return len(packed) / sample_count(ts_ms, values)


def write_sqlite(path: Path, series_id: int, ts_ms: Sequence[int], values: Sequence[float]) -> None:
    sample_count(ts_ms, values)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE samples (series_id INTEGER, ts INTEGER, value REAL)")
    conn.executemany(
        "INSERT INTO samples VALUES (?, ?, ?)",
        ((series_id, t, v) for t, v in zip(ts_ms, values, strict=True)),
    )
    conn.execute("CREATE INDEX samples_by_series_ts ON samples (series_id, ts)")
    conn.commit()
    conn.close()


def sqlite_bytes_per_sample(
    ts_ms: Sequence[int], values: Sequence[float], series_id: int = 0
) -> float:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "samples.db"
        write_sqlite(path, series_id, ts_ms, values)
        return path.stat().st_size / sample_count(ts_ms, values)


def write_parquet(path: Path, ts_ms: Sequence[int], values: Sequence[float]) -> None:
    import pyarrow as pa
    import pyarrow.parquet as pq

    sample_count(ts_ms, values)
    table = pa.table(
        {"ts_ms": pa.array(ts_ms, pa.int64()), "value": pa.array(values, pa.float64())}
    )
    pq.write_table(table, path, compression="zstd")


def parquet_bytes_per_sample(ts_ms: Sequence[int], values: Sequence[float]) -> float:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "samples.parquet"
        write_parquet(path, ts_ms, values)
        return path.stat().st_size / sample_count(ts_ms, values)


def baselines(
    ts_ms: Sequence[int], values: Sequence[float], series_id: int = 0
) -> dict[str, float]:
    return {
        "raw": raw_bytes_per_sample(ts_ms, values),
        "gzip": gzip_bytes_per_sample(ts_ms, values),
        "sqlite": sqlite_bytes_per_sample(ts_ms, values, series_id),
        "parquet": parquet_bytes_per_sample(ts_ms, values),
    }
