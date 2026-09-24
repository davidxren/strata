import platform
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from bench.baselines import NAMES, baselines
from bench.load import read_csv
from bench.synthetic import Dataset, all_datasets

STRATA_COLUMN = "not implemented"
NOTE = "Bytes per sample. Ingest rate and query latency wait for the Store."


@dataclass(frozen=True)
class Row:
    name: str
    samples: int
    bytes_per_sample: dict[str, float]


@dataclass(frozen=True)
class Table:
    label: str
    rows: list[Row]


def measure(dataset: Dataset, series_id: int = 0) -> Row:
    samples = len(dataset.ts_ms)
    return Row(dataset.name, samples, baselines(dataset.ts_ms, dataset.values, series_id))


def synthetic_table(samples: int) -> Table:
    return Table("synthetic", [measure(d) for d in all_datasets(samples)])


def real_tables(data_dir: Path) -> list[Table]:
    return [
        Table(f"real: {path.name}", [measure(d, i) for i, d in enumerate(read_csv(path))])
        for path in sorted(data_dir.glob("*.csv"))
    ]


def platform_line() -> str:
    return (
        f"machine {platform.machine()}, {platform.platform()}, Python {platform.python_version()}"
    )


def render(tables: Sequence[Table]) -> str:
    lines: list[str] = []
    for table in tables:
        lines += [f"## {table.label}", "", NOTE, ""]
        lines.append("| series | samples | " + " | ".join(NAMES) + " | strata |")
        lines.append("|---|---:|" + "---:|" * len(NAMES) + "---|")
        for row in table.rows:
            cells = [f"{row.bytes_per_sample[name]:.2f}" for name in NAMES]
            lines.append(
                f"| {row.name} | {row.samples} | " + " | ".join(cells) + f" | {STRATA_COLUMN} |"
            )
        lines.append("")
    lines.append(platform_line())
    return "\n".join(lines) + "\n"


def report(samples: int, data_dir: Path) -> str:
    return render([synthetic_table(samples), *real_tables(data_dir)])


def run(samples: int, data_dir: Path, out: Path | None) -> str:
    text = report(samples, data_dir)
    print(text, end="")
    if out is not None:
        out.write_text(text)
    return text
