class CameraState:
    def __init__(self, registry, client, on_change = None):
        self.registry = registry
        self.client = client
        self.on_change = on_change

        if on_change:
            self.client.on_change = self._handle_change

    def _handle_change(self, key, value):
        parameter = self.registry.parameter_name(key)

        if parameter is None:
            return

        self.on_change(parameter, self.registry.convert(parameter, value))

    def set(self, parameter, value):

        if not self.registry.is_valid(parameter, value):
            raise ValueError(f"invalid value for {parameter}: {value}")

        if parameter == "sensor_mode":
            self._set_mode(value)
            return

        key = self.registry.redis_key(parameter)
        self.client.set(key, value)

    def _set_mode(self, mode):
        definition = self.registry.modes[mode]
        packing = self.registry.packing

        self.client.set("width", definition["width"])
        self.client.set("height", definition["height"])
        self.client.set("mode",
                        f"{definition['width']}:{definition['height']}:{definition['bit_depth']}:{packing}"
                        )
        self.client.set("cam_init", 1)


    def get(self, parameter):

        key = self.registry.redis_key(parameter)
        value = self.client.get(key)
        
        if value is None:
            return None
        return self.registry.convert(parameter, value)
        
        

