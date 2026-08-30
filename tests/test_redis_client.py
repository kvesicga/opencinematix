import threading

import pytest
import redis

from control.redis_client import RedisClient

TEST_DB = 15
TEST_CHANNEL = "test_controls"
TIMEOUT = 2.0


@pytest.fixture
def clean_db():
    r = redis.Redis(db = TEST_DB, decode_responses = True)

    r.flushdb()
    yield r
    r.flushdb()


class Recorder:
    """Collects callback invocations and lets a test wait for them."""

    def __init__(self):
        self.calls = []
        self.received = threading.Event()

    def __call__(self, key, value):
        self.calls.append((key, value))
        self.received.set()

    def wait(self, timeout = TIMEOUT):
        return self.received.wait(timeout)


@pytest.fixture
def client(clean_db):
    recorder = Recorder()

    c = RedisClient(db = TEST_DB, channel = TEST_CHANNEL, on_change = recorder)
    c.recorder = recorder

    return c


def test_connects_to_given_database():
    c = RedisClient(db = TEST_DB)

    assert c.r.connection_pool.connection_kwargs["db"] == TEST_DB


def test_set_stores_value(client, clean_db):
    client.set("iso", 800)

    assert clean_db.get("iso") == "800"


def test_get_returns_stored_value(client, clean_db):
    clean_db.set("fps", "24")

    assert client.get("fps") == "24"


def test_get_returns_none_for_missing_key(client):
    assert client.get("does_not_exist") is None


def test_set_publishes_key_only(clean_db):
    listener = redis.Redis(db = TEST_DB, decode_responses = True)
    pubsub = listener.pubsub()

    pubsub.subscribe(TEST_CHANNEL)
    pubsub.get_message(timeout = TIMEOUT)

    c = RedisClient(db = TEST_DB, channel = TEST_CHANNEL)
    c.set("iso", 1600)

    message = pubsub.get_message(timeout = TIMEOUT)

    assert message is not None
    assert message["data"] == "iso"


def test_remote_change_triggers_callback(client, clean_db):
    clean_db.set("shutter_a", "180")
    clean_db.publish(TEST_CHANNEL, "shutter_a")

    assert client.recorder.wait()
    assert client.recorder.calls == [("shutter_a", "180")]


def test_own_write_does_not_trigger_callback(client):
    client.set("iso", 400)

    assert not client.recorder.wait(0.5)
    assert client.recorder.calls == []


def test_echo_suppression_consumes_one_message_only(client, clean_db):
    client.set("iso", 400)
    client.recorder.wait(0.5)

    clean_db.set("iso", "800")
    clean_db.publish(TEST_CHANNEL, "iso")

    assert client.recorder.wait()
    assert client.recorder.calls == [("iso", "800")]


def test_subscribe_confirmation_is_ignored(client, clean_db):
    clean_db.publish(TEST_CHANNEL, "fps")

    assert client.recorder.wait()
    assert len(client.recorder.calls) == 1
