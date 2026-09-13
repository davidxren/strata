import struct
from collections.abc import Callable

import pytest

from bench.synthetic import (
    GENERATORS,
    Dataset,
    all_datasets,
    constants,
    random_bits,
    random_walk,
    slow_integers,
)

N = 2000


def packed(values: list[float]) -> list[bytes]:
    return [struct.pack("<d", v) for v in values]


@pytest.mark.parametrize("make", GENERATORS)
def test_same_seed_gives_same_dataset(make: Callable[[int, int], Dataset]) -> None:
    first = make(N, 7)
    second = make(N, 7)
    assert first.ts_ms == second.ts_ms
    assert packed(first.values) == packed(second.values)


@pytest.mark.parametrize("make", GENERATORS)
def test_timestamps_are_one_hertz(make: Callable[[int, int], Dataset]) -> None:
    dataset = make(N, 7)
    assert len(dataset.values) == N
    assert dataset.ts_ms == [1000 * i for i in range(N)]


def test_all_datasets_have_distinct_names() -> None:
    names = [d.name for d in all_datasets(10)]
    assert len(names) == 4
    assert len(set(names)) == 4


def test_random_walk_moves_in_small_steps() -> None:
    values = random_walk(N).values
    assert len(set(values)) > N // 2
    assert all(abs(b - a) < 1.0 for a, b in zip(values, values[1:], strict=False))


def test_slow_integers_are_integral_and_move_by_at_most_one() -> None:
    values = slow_integers(N).values
    assert all(v == int(v) and 40 <= v <= 200 for v in values)
    assert all(abs(b - a) <= 1 for a, b in zip(values, values[1:], strict=False))


def test_constants_never_change() -> None:
    values = constants(N).values
    assert len(set(values)) == 1


def test_random_bits_are_mostly_distinct() -> None:
    assert len(set(packed(random_bits(N).values))) > N * 9 // 10
