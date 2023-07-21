"""Last Track for Niu Integration integration.
    Author: Giovanni P. (@pikka97)
"""
import logging
from typing import final

import httpx

# from homeassistant.components.camera import STATE_IDLE
from homeassistant.components.generic.camera import GenericCamera
from homeassistant.components.generic.const import (
    CONF_CONTENT_TYPE,
    CONF_FRAMERATE,
    CONF_LIMIT_REFETCH_TO_URL_CHANGE,
    CONF_STILL_IMAGE_URL,
    CONF_STREAM_SOURCE,
    GET_IMAGE_TIMEOUT,
)
from homeassistant.const import (
    CONF_AUTHENTICATION,
    CONF_NAME,
    CONF_VERIFY_SSL,
)
from homeassistant.helpers.httpx_client import get_async_client

from .api import NiuApi
from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    niu_auth = entry.data.get(CONF_AUTH, None)
    if niu_auth == None:
        _LOGGER.error(
            "The authenticator of your Niu integration is None.. can not setup the integration..."
        )
        return False

    username = niu_auth[CONF_USERNAME]
    password = niu_auth[CONF_PASSWORD]
    scooter_id = niu_auth[CONF_SCOOTER_ID]

    api = NiuApi(username, password, scooter_id)
    await hass.async_add_executor_job(api.initApi)

    camera_name = api.sensor_prefix + " Last Track Camera"

    entry = {
        CONF_NAME: camera_name,
        CONF_STILL_IMAGE_URL: "https://app-api-fk.niu.com/",
        CONF_STREAM_SOURCE: None,
        CONF_AUTHENTICATION: "basic",
        "username": None,
        "password": None,
        CONF_LIMIT_REFETCH_TO_URL_CHANGE: False,
        CONF_CONTENT_TYPE: "image/jpeg",
        CONF_FRAMERATE: 2,
        CONF_VERIFY_SSL: True,
    }
    async_add_entities([LastTrackCamera(hass, api, entry, camera_name, camera_name)])


class LastTrackCamera(GenericCamera):
    def __init__(self, hass, api, device_info, identifier: str, title: str) -> None:
        self._api = api
        super().__init__(hass, device_info, identifier, title)

    # @property
    # @final
    # def state(self) -> str:
    #     """Return the camera state."""
    #     return STATE_IDLE

    @property
    def is_on(self) -> bool:
        """Return true if on."""
        return self._last_image != b""

    @property
    def device_info(self):
        device_name = "Niu E-scooter"
        dev = {
            "identifiers": {("niu", device_name)},
            "name": device_name,
            "manufacturer": "Niu",
            "model": 1.0,
        }
        return dev

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        get_last_track = lambda: self._api.getDataTrack("track_thumb")
        last_track_url = await self.hass.async_add_executor_job(get_last_track)
        self._still_image_url = last_track_url
        super().async_camera_image(width, height)

    # async def async_camera_image(
    #     self, width: int | None = None, height: int | None = None
    # ) -> bytes | None:
    #     get_last_track = lambda: self._api.getDataTrack("track_thumb")
    #     last_track_url = await self.hass.async_add_executor_job(get_last_track)
    #     # _LOGGER.debug(f"last_track_url url: {last_track_url}")
                
    #     if last_track_url == self._last_url and self._previous_image != b"":
    #         # The path image is the same as before so the image is the same:
    #         return self._previous_image

    #     try:
    #         async_client = get_async_client(self.hass, verify_ssl=self.verify_ssl)
    #         response = await async_client.get(
    #             last_track_url, auth=self._auth, follow_redirects=True, timeout=GET_IMAGE_TIMEOUT
    #         )
    #         response.raise_for_status()
    #         self._last_image = response.content
    #     except httpx.TimeoutException:
    #         _LOGGER.error("Timeout getting camera image from %s", self._name)
    #         return self._last_image
    #     except (httpx.RequestError, httpx.HTTPStatusError) as err:
    #         _LOGGER.error("Error getting new camera image from %s: %s", self._name, err)
    #         return self._last_image

    #     self._last_url = last_track_url
    #     self._previous_image = self._last_image
    #     return self._last_image
