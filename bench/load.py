import csv
from collections.abc import Sequence
from pathlib import Path

from bench.synthetic import SEED, Dataset, constants, random_walk, slow_integers

TIME_COLUMN = "ts_ms"
VALUE_COLUMNS = ("heart_rate", "speed_mps", "cadence_spm", "altitude_m")
HEADER = (TIME_COLUMN, *VALUE_COLUMNS)

SAMPLE_ROWS = 300
SAMPLE_GAPS = {"heart_rate": 7, "altitude_m": 11}


def read_csv(path: Path) -> list[Dataset]:
    ts_ms: list[list[int]] = [[] for _ in VALUE_COLUMNS]
    values: list[list[float]] = [[] for _ in VALUE_COLUMNS]
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = tuple(next(reader, ()))
        if header != HEADER:
            raise ValueError(f"{path}: header {header} is not {HEADER}")
        for row in reader:
            if len(row) != len(HEADER):
                raise ValueError(f"{path}: row {reader.line_num} has {len(row)} cells")
            t = int(row[0])
            for i, cell in enumerate(row[1:]):
                if cell:
                    ts_ms[i].append(t)
                    values[i].append(float(cell))
    return [Dataset(name, ts_ms[i], values[i]) for i, name in enumerate(VALUE_COLUMNS)]


def write_csv(path: Path, columns: Sequence[Dataset]) -> None:
    if tuple(c.name for c in columns) != VALUE_COLUMNS:
        raise ValueError(f"columns {[c.name for c in columns]} are not {VALUE_COLUMNS}")
    lookups = [dict(zip(c.ts_ms, c.values, strict=True)) for c in columns]
    every_ts: set[int] = set()
    for c in columns:
        every_ts.update(c.ts_ms)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for t in sorted(every_ts):
            writer.writerow([t, *(lookup.get(t, "") for lookup in lookups)])


def sample_columns(n: int = SAMPLE_ROWS) -> list[Dataset]:
    sources = (slow_integers(n), random_walk(n), constants(n), random_walk(n, SEED + 1))
    columns = []
    for name, source in zip(VALUE_COLUMNS, sources, strict=True):
        gap = SAMPLE_GAPS.get(name, 0)
        keep = [i for i in range(n) if not gap or i % gap]
        ts_ms = [source.ts_ms[i] for i in keep]
        values = [source.values[i] for i in keep]
        columns.append(Dataset(name, ts_ms, values))
    return columns
