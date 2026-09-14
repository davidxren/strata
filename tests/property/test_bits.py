# Contract for strata/bits.py, MSB-first over a Python int accumulator:
#
#   class BitWriter:
#       def __init__(self) -> None
#       def write_bit(self, bit: int) -> None
#           bit is 0 or 1, else ValueError
#       def write_bits(self, value: int, width: int) -> None
#           1 <= width <= 64 and 0 <= value < 2**width, else ValueError
#       def to_bytes(self) -> bytes
#           the last byte is padded with zero bits on the right
#
#   class BitReader:
#       def __init__(self, data: bytes) -> None
#       def read_bit(self) -> int
#           EOFError once every bit, padding included, has been read
#       def read_bits(self, width: int) -> int
#           1 <= width <= 64 else ValueError; EOFError if fewer than width bits remain
#       def at_end(self) -> bool
#           True once every bit, padding included, has been read

import pytest
from hypothesis import given
from hypothesis import strategies as st

from strata.bits import BitReader, BitWriter

widths = st.integers(min_value=1, max_value=64)
bits = st.integers(min_value=0, max_value=1)


def field(width: int) -> st.SearchStrategy[tuple[int, int]]:
    return st.tuples(st.just(width), st.integers(min_value=0, max_value=2**width - 1))


fields = widths.flatmap(field)
narrow_fields = st.one_of(st.just(1), widths).flatmap(field)


def write_all(items: list[tuple[int, int]]) -> bytes:
    writer = BitWriter()
    for width, value in items:
        writer.write_bits(value, width)
    return writer.to_bytes()


@given(st.lists(fields))
def test_fields_round_trip(items: list[tuple[int, int]]) -> None:
    reader = BitReader(write_all(items))
    assert [reader.read_bits(width) for width, _ in items] == [value for _, value in items]


@given(st.lists(bits))
def test_single_bits_round_trip(values: list[int]) -> None:
    writer = BitWriter()
    for bit in values:
        writer.write_bit(bit)
    reader = BitReader(writer.to_bytes())
    assert [reader.read_bit() for _ in values] == values


@given(st.lists(st.tuples(narrow_fields, st.booleans())))
def test_bit_and_field_writes_interleave(items: list[tuple[tuple[int, int], bool]]) -> None:
    writer = BitWriter()
    for (width, value), single in items:
        if single and width == 1:
            writer.write_bit(value)
        else:
            writer.write_bits(value, width)
    reader = BitReader(writer.to_bytes())
    for (width, value), single in items:
        if single and width == 1:
            assert reader.read_bit() == value
        else:
            assert reader.read_bits(width) == value


@given(fields)
def test_field_reads_back_msb_first(item: tuple[int, int]) -> None:
    width, value = item
    writer = BitWriter()
    writer.write_bits(value, width)
    reader = BitReader(writer.to_bytes())
    expected = [(value >> (width - 1 - i)) & 1 for i in range(width)]
    assert [reader.read_bit() for _ in range(width)] == expected


@given(st.lists(fields))
def test_byte_length_is_bit_count_rounded_up(items: list[tuple[int, int]]) -> None:
    total = sum(width for width, _ in items)
    assert len(write_all(items)) == (total + 7) // 8


@given(st.lists(fields))
def test_padding_reads_as_zero_then_at_end(items: list[tuple[int, int]]) -> None:
    data = write_all(items)
    reader = BitReader(data)
    for width, _ in items:
        reader.read_bits(width)
    padding = len(data) * 8 - sum(width for width, _ in items)
    assert reader.at_end() == (padding == 0)
    assert [reader.read_bit() for _ in range(padding)] == [0] * padding
    assert reader.at_end()
    with pytest.raises(EOFError):
        reader.read_bit()


def test_single_bit() -> None:
    writer = BitWriter()
    writer.write_bit(1)
    data = writer.to_bytes()
    assert data == b"\x80"
    reader = BitReader(data)
    assert reader.read_bit() == 1
    assert not reader.at_end()
    assert reader.read_bits(7) == 0
    assert reader.at_end()


def test_sixty_four_bit_field_at_both_extremes() -> None:
    writer = BitWriter()
    writer.write_bits(0, 64)
    writer.write_bits(2**64 - 1, 64)
    data = writer.to_bytes()
    assert data == b"\x00" * 8 + b"\xff" * 8
    reader = BitReader(data)
    assert reader.read_bits(64) == 0
    assert reader.read_bits(64) == 2**64 - 1
    assert reader.at_end()


def test_stream_ending_mid_byte() -> None:
    writer = BitWriter()
    writer.write_bits(0b101, 3)
    data = writer.to_bytes()
    assert data == b"\xa0"
    reader = BitReader(data)
    assert reader.read_bits(3) == 0b101
    assert not reader.at_end()
    assert reader.read_bits(5) == 0
    assert reader.at_end()


def test_field_spans_byte_boundary_msb_first() -> None:
    writer = BitWriter()
    writer.write_bits(0xABC, 12)
    assert writer.to_bytes() == b"\xab\xc0"


def test_empty_stream() -> None:
    assert BitWriter().to_bytes() == b""
    reader = BitReader(b"")
    assert reader.at_end()
    with pytest.raises(EOFError):
        reader.read_bit()


def test_reading_past_end_raises() -> None:
    reader = BitReader(b"\xff")
    assert reader.read_bits(8) == 0xFF
    with pytest.raises(EOFError):
        reader.read_bit()
    with pytest.raises(EOFError):
        BitReader(b"\xff").read_bits(9)


@pytest.mark.parametrize(("value", "width"), [(2, 1), (-1, 4), (1 << 8, 8), (1 << 64, 64)])
def test_write_bits_rejects_value_outside_width(value: int, width: int) -> None:
    with pytest.raises(ValueError):
        BitWriter().write_bits(value, width)


@pytest.mark.parametrize("width", [0, 65, -1])
def test_width_outside_one_to_sixty_four_raises(width: int) -> None:
    with pytest.raises(ValueError):
        BitWriter().write_bits(0, width)
    with pytest.raises(ValueError):
        BitReader(bytes(16)).read_bits(width)


@pytest.mark.parametrize("bit", [2, -1])
def test_write_bit_rejects_non_bit(bit: int) -> None:
    with pytest.raises(ValueError):
        BitWriter().write_bit(bit)
