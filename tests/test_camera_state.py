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
