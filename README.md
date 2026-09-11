# strata

A storage engine for sensor time series. Python, standard library only.

I'm building it to store what my [running engine](https://github.com/davidxren/YOUR-RUNNING-REPO) produces: heart rate, pace, cadence, and altitude at one sample per second, from my own Garmin recordings. That workload is the reason for every design choice in here, and it is what the engine gets benchmarked on.

The interesting parts are the codec and the recovery path. Samples are compressed with the scheme from Facebook's Gorilla paper (delta-of-delta timestamps, XOR'd floats), which is built for exactly this: values that barely move between samples and timestamps that tick at a fixed rate. Writes go through a write-ahead log, get compacted into checksummed blocks, and recovery on open verifies every checksum and replays the log. A store that fails a checksum raises. It never quietly returns less data than it was given.

## What it is not

One writer, one process, one directory. Series are integer ids. There are no tags, no query language, no retention or downsampling, no replication, no network API. None of that is planned for v1.

## Status

Nothing works yet. This section changes as milestones land.

- M1, codec: bit I/O and Gorilla encode/decode, property tested. Not started.
- M2, blocks and index, range queries. Not started.
- M3, write-ahead log, recovery, crash test harness. Not started.
- M4, benchmarks against SQLite and Parquet on the real dataset. Not started.

## Numbers

None yet. When there are, they come from `strata bench --out bench.md` and get pasted here unchanged, with the machine, OS, and Python version that produced them.

## Running it

    make setup
    make test
    make lint

Python 3.12. Dev dependencies are pytest, hypothesis, ruff, and mypy. The engine itself imports nothing outside the standard library; the benchmark baselines (numpy, pyarrow) are only pulled in by `make bench`.

## Design

`docs/DESIGN.md` covers the encoding, the on-disk layout, durability and recovery, and the fault model the crash tests use. Each section is written before the code it describes, and the code is checked against it.

## Reading

Pelkonen et al., "Gorilla: A Fast, Scalable, In-Memory Time Series Database", VLDB 2015, is the source for the codec. `docs/reading.md` has the rest.

## License

MIT
