class CameraState:
    def __init__(self, registry, client):
        self.registry = registry
        self.client = client

    def set(self, parameter, value):
        key = self.registry.redis_key(parameter)
        self.client.set(key, value)
