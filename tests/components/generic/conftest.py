"""Test fixtures for the generic component."""

from __future__ import annotations

from collections.abc import Generator
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from PIL import Image
import pytest
import respx

from homeassistant import config_entries
from homeassistant.components.generic.const import DOMAIN
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


@pytest.fixture(scope="package")
def fakeimgbytes_png() -> bytes:
    """Fake image in RAM for testing."""
    buf = BytesIO()
    Image.new("RGB", (1, 1)).save(buf, format="PNG")
    return bytes(buf.getbuffer())


@pytest.fixture(scope="package")
def fakeimgbytes_jpg() -> bytes:
    """Fake image in RAM for testing."""
    buf = BytesIO()  # fake image in ram for testing.
    Image.new("RGB", (1, 1)).save(buf, format="jpeg")
    return bytes(buf.getbuffer())


@pytest.fixture(scope="package")
def fakeimgbytes_svg() -> bytes:
    """Fake image in RAM for testing."""
    return bytes(
        '<svg xmlns="http://www.w3.org/2000/svg"><circle r="50"/></svg>',
        encoding="utf-8",
    )


@pytest.fixture(scope="package")
def fakeimgbytes_gif() -> bytes:
    """Fake image in RAM for testing."""
    buf = BytesIO()  # fake image in ram for testing.
    Image.new("RGB", (1, 1)).save(buf, format="gif")
    return bytes(buf.getbuffer())


@pytest.fixture
def fakeimg_png(fakeimgbytes_png: bytes) -> Generator[None]:
    """Set up respx to respond to test url with fake image bytes."""
    respx.get("http://127.0.0.1/testurl/1", name="fake_img1").respond(
        stream=fakeimgbytes_png
    )
    respx.get("http://127.0.0.1/testurl/2", name="fake_img2").respond(
        stream=fakeimgbytes_png
    )
    yield
    respx.pop("fake_img1")
    respx.pop("fake_img2")


@pytest.fixture
def fakeimg_gif(fakeimgbytes_gif: bytes) -> Generator[None]:
    """Set up respx to respond to test url with fake image bytes."""
    respx.get("http://127.0.0.1/testurl/1", name="fake_img").respond(
        stream=fakeimgbytes_gif
    )
    yield
    respx.pop("fake_img")


@pytest.fixture(name="mock_create_stream")
def mock_create_stream(hass: HomeAssistant) -> Generator[AsyncMock]:
    """Mock create stream."""
    mock_stream = MagicMock()
    mock_stream.hass = hass
    mock_provider = Mock()
    mock_provider.part_recv = AsyncMock()
    mock_provider.part_recv.return_value = True
    mock_stream.add_provider.return_value = mock_provider
    mock_stream.start = AsyncMock()
    mock_stream.stop = AsyncMock()
    mock_stream.endpoint_url.return_value = "http://127.0.0.1/nothing"
    with patch(
        "homeassistant.components.generic.config_flow.create_stream",
        return_value=mock_stream,
    ) as mock_create_stream:
        yield mock_create_stream


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Mock setup entry."""
    with patch(
        "homeassistant.components.generic.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture(name="user_flow")
async def user_flow_fixture(hass: HomeAssistant) -> ConfigFlowResult:
    """Initiate a user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    return result


@pytest.fixture(name="config_entry")
def config_entry_fixture(hass: HomeAssistant) -> MockConfigEntry:
    """Define a config entry fixture."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Camera",
        unique_id="abc123",
        data={},
        options={
            "still_image_url": "http://joebloggs:letmein1@example.com/secret1/file.jpg?pw=qwerty",
            "stream_source": "http://janebloggs:letmein2@example.com/stream",
            "username": "johnbloggs",
            "password": "letmein123",
            "limit_refetch_to_url_change": False,
            "authentication": "basic",
            "framerate": 2.0,
            "verify_ssl": True,
            "content_type": "image/jpeg",
        },
        version=1,
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture(name="setup_entry")
async def setup_entry_fixture(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> MockConfigEntry:
    """Set up a config entry ready to be used in tests."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
