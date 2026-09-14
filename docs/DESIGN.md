Design of strata, a single-writer, append-only storage engine for sensor time series; each section is written before the code it describes.

## Encoding

*Which bits leave the encoder for every timestamp delta-of-delta range and every XOR value, why the signed ranges are asymmetric, why leading zeros are capped at 31, why the meaningful length is stored minus one, and which inputs raise instead of encoding.*

## On-disk layout

*Every byte of MANIFEST, wal.log, blocks.dat, index.dat, and LOCK, which fields each checksum covers, why blocks and index entries are append-only, and why a query can dedupe equal timestamps at read time.*

## Durability and recovery

*What flush promises, the exact compaction write order with the fsyncs, what a crash between each pair of steps leaves on disk, and how open rebuilds a store that still satisfies D, C, and I.*

## Fault model

*What FaultyFS may do to pending bytes, to the last write of one file, and to a rename before its directory fsync, which real filesystem behaviors each of those stands in for, and which failures the model does not cover.*
