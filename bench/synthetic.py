import random
import struct
from collections.abc import Callable
from dataclasses import dataclass

SEED = 1
STEP_MS = 1000


@dataclass(frozen=True)
class Dataset:
    name: str
    ts_ms: list[int]
    values: list[float]


def timestamps(n: int) -> list[int]:
    return [STEP_MS * i for i in range(n)]


def random_walk(n: int, seed: int = SEED) -> Dataset:
    rng = random.Random(seed)
    values: list[float] = []
    x = 0.0
    for _ in range(n):
        x += rng.gauss(0.0, 0.1)
        values.append(x)
    return Dataset("random_walk", timestamps(n), values)


def slow_integers(n: int, seed: int = SEED) -> Dataset:
    rng = random.Random(seed)
    values: list[float] = []
    x = 140
    for _ in range(n):
        x = min(200, max(40, x + rng.choice((-1, 0, 0, 0, 1))))
        values.append(float(x))
    return Dataset("slow_integers", timestamps(n), values)


def constants(n: int, seed: int = SEED) -> Dataset:
    value = float(random.Random(seed).randint(1, 1000))
    return Dataset("constants", timestamps(n), [value] * n)


def random_bits(n: int, seed: int = SEED) -> Dataset:
    rng = random.Random(seed)
    values: list[float] = [
        struct.unpack("<d", rng.getrandbits(64).to_bytes(8, "little"))[0] for _ in range(n)
    ]
    return Dataset("random_bits", timestamps(n), values)


GENERATORS: tuple[Callable[[int, int], Dataset], ...] = (
    random_walk,
    slow_integers,
    constants,
    random_bits,
)


def all_datasets(n: int, seed: int = SEED) -> list[Dataset]:
    return [make(n, seed) for make in GENERATORS]
