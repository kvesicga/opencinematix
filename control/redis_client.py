import redis
import threading

CHANNEL_CONTROLS = "cp_controls"


class RedisClient:
    def __init__(self, host="127.0.0.1", port=6379, on_change=None):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)

        self.local_updates = set()
        self.lock = threading.Lock()

        self.on_change = on_change

        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(CHANNEL_CONTROLS)
        self.listener = threading.Thread(target=self._listen, daemon=True)
        self.listener.start()

    def get(self, key):
        return self.r.get(key)

    def set(self, key, value):
        with self.lock:
            self.local_updates.add(key)
        self.r.set(key, value)
        self.r.publish(CHANNEL_CONTROLS, key)

    def _listen(self):
        for message in self.pubsub.listen():
            if message["type"] != "message":
                continue
            key = message["data"]
            with self.lock:
                if key in self.local_updates:
                    self.local_updates.discard(key)
                    continue

            if self.on_change:
                self.on_change(key, self.get(key))
