import pytest

from core.hal.quadrature import QuadratureDecoder


@pytest.fixture
def decoder():
    return QuadratureDecoder()


def test_starts_at_rest(decoder):
    assert decoder.update(1, 1) == 0


def test_first_step_clockwise(decoder):
    decoder.update(1, 1)

    assert decoder.update(0, 1) == 1


def test_first_step_counter_clockwise(decoder):
    decoder.update(1, 1)

    assert decoder.update(1, 0) == -1


def test_invalid_transition_is_discarded(decoder):
    decoder.update(1, 1)

    assert decoder.update(0, 0) == 0
