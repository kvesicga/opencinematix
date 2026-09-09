class CameraState:
    def __init__(self, registry, client):
        self.registry = registry
        self.client = client

    def set(self, parameter, value):
        
        if not self.registry.is_valid(parameter, value):
            raise ValueError(f"invalid value for {parameter}: {value}")

        key = self.registry.redis_key(parameter)
        self.client.set(key, value)