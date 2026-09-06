from core.parameters import ParameterRegistry 


def test_loads_all_parameters(): 
    registry = ParameterRegistry("config/parameters.yaml")

    assert len(registry.parameters) == 6 


def test_loads_sensor_modes():
    registry = ParameterRegistry("config/parameters.yaml")

    assert len(registry.modes) == 7
    assert registry.default_mode == "2028x1080x12"
