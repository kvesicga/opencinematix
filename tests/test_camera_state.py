import pytest
import redis

from control.camera_state import CameraState
from control.redis_client import RedisClient
from core.parameters import ParameterRegistry

CONFIG = "config/parameters.yaml"
TEST_DB = 15
TEST_CHANNEL = "test_camera"


@pytest.fixture
def clean_db():
    r = redis.Redis(db = TEST_DB, decode_responses = True)

    r.flushdb()
    yield r
    r.flushdb()


@pytest.fixture
def camera(clean_db):
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
