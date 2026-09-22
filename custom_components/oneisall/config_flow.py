"""Config flow for the Oneisall Pet Feeder integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL_VERSION,
    DEFAULT_NAME,
    DEFAULT_PROTOCOL_VERSION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Required(CONF_LOCAL_KEY): cv.string,
        vol.Required(CONF_PROTOCOL_VERSION, default=DEFAULT_PROTOCOL_VERSION): vol.In(
            ["3.1", "3.2", "3.3", "3.4", "3.5"]
        ),
    }
)


async def _test_connection(hass, data: dict[str, Any]) -> None:
    """Raise on failure. Runs in the executor since tinytuya is blocking/sync."""
    import tinytuya

    def _connect() -> dict:
        device = tinytuya.Device(
            dev_id=data[CONF_DEVICE_ID],
            address=data[CONF_HOST],
            local_key=data[CONF_LOCAL_KEY],
            version=float(data[CONF_PROTOCOL_VERSION]),
        )
        return device.status()

    result = await hass.async_add_executor_job(_connect)
    if not result or "dps" not in result:
        raise CannotConnect(f"No usable response from feeder: {result}")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Oneisall feeder."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()

            try:
                await _test_connection(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error validating Oneisall feeder")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect to the feeder."""
