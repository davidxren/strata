# Interview questions

## 1. Why delta-of-delta for timestamps instead of delta? What is the cost of a 1 Hz stream per sample?

Answer:

## 2. Why does XOR compress slowly changing floats? Walk through the IEEE 754 layout and what the leading and trailing zeros mean.

Answer:

## 3. What happens on power loss between writing a block and writing its index entry? Between the index entry and truncating the WAL? Show that D and C still hold.

Answer:

## 4. Why a checksum per record and per block rather than per file?

Answer:

## 5. Why must you fsync the directory after creating or renaming a file?

Answer:

## 6. GNU Make 3.81 on this Mac ignores an exported PATH when it execs a recipe line directly. Why did that break the first Makefile, and why does the current one not depend on PATH at all?

Answer:

## 7. Hypothesis loads its own built-in "ci" profile whenever the CI environment variable is set, and profiles registered without a parent inherit from whatever is active at import. What does that mean for deadline and derandomize when the ci profile runs on GitHub Actions versus locally?

Answer:

## 8. The handoff's gitignore entry `data/` is unanchored. What happens to a public sample checked in under tests/data/, and what is the one-character fix if that ever matters?

Answer:
