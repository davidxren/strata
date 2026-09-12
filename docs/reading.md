# Reading

1. Pelkonen et al., "Gorilla: A Fast, Scalable, In-Memory Time Series Database", VLDB 2015, sections 4.1 and 4.4. https://www.vldb.org/pvldb/vol8/p1816-teller.pdf
   The exact bit patterns for delta-of-delta timestamps and XOR values, and the on-disk structure. Read before writing the Encoding section.
2. Fabian Reinartz, "Writing a Time Series Database from Scratch". https://fabxc.org/tsdb/
   Chunks, index, write-ahead log, and why append-only wins for time series.
3. Dan Luu, "Files are hard". https://danluu.com/file-consistency/
   What fsync does and does not promise, and how often real programs get it wrong.
4. Pillai et al., "All File Systems Are Not Created Equal: On the Complexity of Crafting Crash-Consistent Applications", OSDI 2014. https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-pillai.pdf
   The crash-vulnerability taxonomy, which the fault model is built on.
5. IEEE 754 double layout. https://en.wikipedia.org/wiki/Double-precision_floating-point_format
   Sign, 11-bit exponent, 52-bit mantissa, NaN payloads, signed zero, subnormals.
6. A short primer on write-ahead logging and ARIES-style recovery, from any database systems textbook.
   Why the log is written before the data, and what replay must be idempotent against.
