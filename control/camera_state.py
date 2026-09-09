class CameraState:
    def __init__(self, registry, client):
        self.registry = registry
        self.client = client

    def set(self, parameter, value):

        if not self.registry.is_valid(parameter, value):
            raise ValueError(f"invalid value for {parameter}: {value}")

        key = self.registry.redis_key(parameter)
        self.client.set(key, value)

    def get(self, parameter):

        key = self.registry.redis_key(parameter)
        value = self.client.get(key)
        
        if value is None:
            return None
        return self.registry.convert(parameter, value)
        
        

