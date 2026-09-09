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
