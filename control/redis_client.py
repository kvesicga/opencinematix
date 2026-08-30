import redis
import threading

CHANNEL_CONTROLS = "cp_controls"                                                  # cinepi-raw listens to this port 

class RedisClient: 
    def __init__(self, host = '127.0.0.1', port = 6379):
        self.r = redis.Redis(host = host, port = port, decode_responses = True)
        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(CHANNEL_CONTROLS)
        self.listener = threading.Thread(target = self._listen, daemon = True)
        self.listener.start()

    def get(self, key):
            return self.r.get(key)

    def set(self, key, value):
        self.r.set(key, value)
        self.r.publish(CHANNEL_CONTROLS, key)

    def _listen(self):
         for message in self.pubsub.listen():
              if message["type"] != "message":
                   continue
              key = message["data"]
              print(f"changed: {key} = {self.get(key)}")
