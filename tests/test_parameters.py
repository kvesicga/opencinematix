import pytest

from core.parameters import ParameterRegistry

CONFIG = "config/parameters.yaml"


@pytest.fixture
def registry():
    return ParameterRegistry(CONFIG)


def test_loads_all_parameters(registry):
    assert len(registry.parameters) == 6


def test_loads_sensor_modes(registry):
    assert len(registry.modes) == 7
    assert registry.default_mode == "2028x1080x12"


def test_resolves_name_to_redis_key(registry):
    assert registry.redis_key("shutter_angle") == "shutter_a"
    assert registry.redis_key("iso") == "iso"


def test_unknown_name_raises(registry):
    with pytest.raises(KeyError):
        registry.redis_key("does_not_exist")


def test_accepts_value_from_list(registry):
    assert registry.is_valid("iso", 800)
    assert registry.is_valid("shutter_angle", 180.0)


def test_rejects_value_outside_list(registry):
    assert not registry.is_valid("iso", 6400)
    assert not registry.is_valid("shutter_angle", 200.0)


def test_validates_enum_against_keys(registry):
    assert registry.is_valid("white_balance", 1)
    assert not registry.is_valid("white_balance", 99)


def test_validates_mode_against_sensor(registry):
    assert registry.is_valid("sensor_mode", "2028x1080x12")
    assert not registry.is_valid("sensor_mode", "8000x4000x12")


def test_converts_text_to_int(registry):
    assert registry.convert("iso", "800") == 800


def test_converts_text_to_float(registry):
    assert registry.convert("shutter_angle", "180.0") == 180.0


def test_converts_enum_to_int(registry):
    assert registry.convert("white_balance", "1") == 1


def test_converts_text_to_bool(registry):
    assert registry.convert("is_recording", "1") is True
    assert registry.convert("is_recording", "0") is False


def test_mode_stays_text(registry):
    assert registry.convert("sensor_mode", "2028x1080x12") == "2028x1080x12"


def test_unknown_type_raises(registry):
    registry.parameters["broken"] = {"key": "broken", "type": "itn"}

    with pytest.raises(ValueError):
        registry.convert("broken", "1")
