import redis

CHANNEL_CONTROLS = "cp_controls"                                                  # cinepi-raw listens to this port 

class RedisClient: 
    def __init__(self, host = '127.0.0.1', port = 6379):
        self.r = redis.Redis(host = host, port = port, decode_responses = True)

