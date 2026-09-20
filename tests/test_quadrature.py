import pytest

from core.hal.quadrature import QuadratureDecoder


@pytest.fixture
def decoder():
    return QuadratureDecoder()


def test_starts_at_rest(decoder):
    assert decoder.update(1, 1) == 0


def test_first_quarter_reports_nothing(decoder):
    assert decoder.update(0, 1) == 0


def test_invalid_transition_is_discarded(decoder):
    decoder.update(1, 1)

    assert decoder.update(0, 0) == 0


CW = [(0, 1), (0, 0), (1, 0), (1, 1)]
CCW = [(1, 0), (0, 0), (0, 1), (1, 1)]


def feed(decoder, sequence):
    return [decoder.update(a, b) for a, b in sequence]


def test_full_detent_reports_one_step(decoder):
    assert feed(decoder, CW) == [0, 0, 0, 1]


def test_full_detent_counter_clockwise(decoder):
    assert feed(decoder, CCW) == [0, 0, 0, -1]


def test_partial_rotation_reports_nothing(decoder):
    assert feed(decoder, CW[:3]) == [0, 0, 0]


def test_several_detents_accumulate(decoder):
    assert sum(feed(decoder, CW * 3)) == 3
