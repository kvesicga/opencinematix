import yaml
from pathlib import Path


class ParameterRegistry:
    def __init__(self, path):
        with open(path) as f:
            data = yaml.safe_load(f)

        self.parameters = data["parameters"]


        sensor = data["sensor"]
        sensor_config = Path(path).parent / "sensors" / f"{sensor}.yaml"
        
        with open(sensor_config) as fn:
            sensor_data = yaml.safe_load(fn)

        self.modes = sensor_data["modes"]
        self.default_mode = sensor_data["default_mode"]
        self.packing = sensor_data["packing"]
        
    def redis_key(self, parameter):
        return self.parameters[parameter]["key"]

    def is_valid(self, parameter, value):
        definition = self.parameters[parameter]

        if definition["type"] == "mode":
            return value in self.modes

        if definition["type"] == "bool":
            return isinstance(value, bool)
        
        else:
            return value in definition["values"]


    def convert(self, parameter, value):
        definition = self.parameters[parameter]
        
        if definition["type"] == "mode":
            return value
        
        if definition["type"] == "bool":
            if value == "1":
                return True
            return False

        if definition["type"] == "int" or definition["type"] == "enum":
            return int(value)

        if definition["type"] == "float":
            return float(value)

        raise ValueError(f"unknown type: {definition['type']}")

        


