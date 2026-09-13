import threading

import pytest
import redis

from control.camera_state import CameraState
from control.redis_client import RedisClient
from core.parameters import ParameterRegistry

CONFIG = "config/parameters.yaml"
TEST_DB = 15
TEST_CHANNEL = "test_camera"
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

    def __call__(self, parameter, value):
        self.calls.append((parameter, value))
        self.received.set()

    def wait(self, timeout = TIMEOUT):
        return self.received.wait(timeout)


@pytest.fixture
def camera(clean_db):
    registry = ParameterRegistry(CONFIG)
    client = RedisClient(db = TEST_DB, channel = TEST_CHANNEL)

    return CameraState(registry, client)


@pytest.fixture
def watched_camera(clean_db):
    recorder = Recorder()
    registry = ParameterRegistry(CONFIG)
    client = RedisClient(db = TEST_DB, channel = TEST_CHANNEL)

    state = CameraState(registry, client, on_change = recorder)
    state.recorder = recorder

    return state


@pytest.fixture
def other_client(clean_db):
    registry = ParameterRegistry(CONFIG)
    client = RedisClient(db = TEST_DB, channel = TEST_CHANNEL)

    return CameraState(registry, client)


def test_set_writes_to_the_mapped_redis_key(camera, clean_db):
    camera.set("shutter_angle", 180.0)

    assert clean_db.get("shutter_a") == "180.0"


def test_set_rejects_invalid_value(camera):
    with pytest.raises(ValueError):
        camera.set("iso", 6400)


def test_rejected_value_is_not_written(camera, clean_db):
    with pytest.raises(ValueError):
        camera.set("iso", 6400)

    assert clean_db.get("iso") is None


def test_get_returns_converted_value(camera, clean_db):
    clean_db.set("iso", "800")

    assert camera.get("iso") == 800


def test_get_reads_the_mapped_redis_key(camera, clean_db):
    clean_db.set("shutter_a", "180.0")

    assert camera.get("shutter_angle") == 180.0


def test_get_returns_none_for_unset_key(camera):
    assert camera.get("iso") is None


def test_set_then_get_round_trip(camera):
    camera.set("iso", 1600)

    assert camera.get("iso") == 1600


def test_mode_is_written_in_colon_format(camera, clean_db):
    camera.set("sensor_mode", "2028x1520x12")

    assert clean_db.get("mode") == "2028:1520:12:P"


def test_mode_writes_dimensions_separately(camera, clean_db):
    camera.set("sensor_mode", "2028x1520x12")

    assert clean_db.get("width") == "2028"
    assert clean_db.get("height") == "1520"


def test_mode_triggers_camera_reinit(camera, clean_db):
    camera.set("sensor_mode", "2028x1520x12")

    assert clean_db.get("cam_init") is not None


def test_remote_change_reports_parameter_name_and_type(watched_camera, other_client):
    other_client.set("shutter_angle", 90.0)

    assert watched_camera.recorder.wait()
    assert watched_camera.recorder.calls == [("shutter_angle", 90.0)]


def test_remote_int_change_is_converted(watched_camera, other_client):
    other_client.set("iso", 1600)

    assert watched_camera.recorder.wait()
    assert watched_camera.recorder.calls == [("iso", 1600)]


def test_own_write_is_not_reported(watched_camera):
    watched_camera.set("iso", 800)

    assert not watched_camera.recorder.wait(0.5)
    assert watched_camera.recorder.calls == []


def test_unknown_key_is_ignored(watched_camera, clean_db):
    clean_db.set("frameCount", "42")
    clean_db.publish(TEST_CHANNEL, "frameCount")

    assert not watched_camera.recorder.wait(0.5)
    assert watched_camera.recorder.calls == []


def test_bool_is_written_as_one_or_zero(camera, clean_db):
    camera.set("is_recording", True)
    assert clean_db.get("is_recording") == "1"

    camera.set("is_recording", False)
    assert clean_db.get("is_recording") == "0"


def test_bool_round_trip(camera):
    camera.set("is_recording", True)

    assert camera.get("is_recording") is True


def test_live_parameter_can_change_while_recording(camera, clean_db):
    clean_db.set("is_recording", "1")

    camera.set("iso", 1600)

    assert clean_db.get("iso") == "1600"


def test_static_parameter_is_blocked_while_recording(camera, clean_db):
    clean_db.set("is_recording", "1")

    with pytest.raises(RuntimeError):
        camera.set("sensor_mode", "2028x1520x12")


def test_blocked_parameter_is_not_written(camera, clean_db):
    clean_db.set("is_recording", "1")

    with pytest.raises(RuntimeError):
        camera.set("fps", 50)

    assert clean_db.get("fps") is None


def test_static_parameter_allowed_when_not_recording(camera, clean_db):
    clean_db.set("is_recording", "0")

    camera.set("fps", 50)

    assert clean_db.get("fps") == "50"


def test_static_parameter_allowed_when_key_absent(camera, clean_db):
    camera.set("fps", 50)

    assert clean_db.get("fps") == "50"
