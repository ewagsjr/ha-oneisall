"""The Oneisall Pet Feeder integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL_VERSION,
    DOMAIN,
    UPDATE_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

SERVICE_SET_RAW_DP = "set_raw_dp"
SET_RAW_DP_SCHEMA = vol.Schema(
    {
        vol.Required("entry_id"): cv.string,
        vol.Required("dp"): cv.string,
        vol.Required("value"): vol.Any(bool, int, float, str),
    }
)


class OneisallCoordinator(DataUpdateCoordinator[dict]):
    """Polls the feeder's raw DPS over the local Tuya protocol."""

    def __init__(self, hass: HomeAssistant, device) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self.device = device

    async def _async_update_data(self) -> dict:
        result = await self.hass.async_add_executor_job(self.device.status)
        if not result or "dps" not in result:
            raise UpdateFailed(f"Unexpected response from feeder: {result}")
        # The feeder reports only the datapoints that changed since the last
        # response, so merge onto the previous snapshot rather than replacing
        # it - otherwise battery, status and the rest vanish between feeds.
        return {**(self.data or {}), **result["dps"]}

    async def async_set_dp(self, dp: str, value) -> None:
        await self.hass.async_add_executor_job(self.device.set_value, dp, value)
        self.async_set_updated_data({**(self.data or {}), dp: value})
        await self.async_request_refresh()

    async def async_set_multiple(self, values: dict) -> None:
        await self.hass.async_add_executor_job(self.device.set_multiple_values, values)
        self.async_set_updated_data({**(self.data or {}), **values})
        await self.async_request_refresh()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an Oneisall feeder from a config entry."""
    import tinytuya

    device = tinytuya.Device(
        dev_id=entry.data[CONF_DEVICE_ID],
        address=entry.data[CONF_HOST],
        local_key=entry.data[CONF_LOCAL_KEY],
        version=float(entry.data[CONF_PROTOCOL_VERSION]),
        # A battery-backed feeder sleeps its radio between reports, which
        # leaves stale queued frames on a persistent socket. A fresh LAN
        # request each poll gives a complete, current DPS snapshot.
        persist=False,
    )

    coordinator = OneisallCoordinator(hass, device)
    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed as err:
        raise ConfigEntryNotReady(
            f"Could not reach the feeder at {entry.data[CONF_HOST]}: {err}"
        ) from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _handle_set_raw_dp(call: ServiceCall) -> None:
        target: OneisallCoordinator = hass.data[DOMAIN][call.data["entry_id"]]
        await target.async_set_dp(call.data["dp"], call.data["value"])

    hass.services.async_register(
        DOMAIN, SERVICE_SET_RAW_DP, _handle_set_raw_dp, schema=SET_RAW_DP_SCHEMA
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
