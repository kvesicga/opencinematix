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
        
    def redis_key(self, parameter):
        return self.parameters[parameter]["key"]




       



