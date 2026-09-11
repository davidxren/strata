# strata

A storage engine for sensor time series. Python 3.12, standard library only.

strata stores fixed-rate sensor samples (a series id, a millisecond timestamp, a float value) and answers range queries over a series. Samples are compressed with the Gorilla scheme (delta-of-delta timestamps, XOR-encoded values), written through a write-ahead log, and compacted into checksummed immutable blocks. Recovery on open verifies every checksum and replays the log. A store that fails a checksum raises rather than returning partial data.

## Scope

One writer, one process, one directory. Series are integer ids. No tags, no query language, no retention or downsampling, no replication, no network API.

## Status

Nothing works yet.

- M1, codec: bit I/O and Gorilla encode/decode, property tested. Not started.
- M2, blocks, index, range queries. Not started.
- M3, write-ahead log, recovery, crash test harness. Not started.
- M4, benchmarks against SQLite and Parquet. Not started.

## Benchmarks

Not measured yet. Numbers are produced by `strata bench --out bench.md` and reported with the machine, OS, and Python version that produced them.

## Development

    make setup
    make test
    make lint

Dev dependencies: pytest, hypothesis, ruff, mypy. Benchmark dependencies (numpy, pyarrow) are only installed by `make bench`. The engine has no runtime dependencies.

## Design

`docs/DESIGN.md` covers the encoding, the on-disk layout, durability and recovery, and the fault model used by the crash tests.

## References

Pelkonen et al., "Gorilla: A Fast, Scalable, In-Memory Time Series Database", VLDB 2015.

## License

MIT
