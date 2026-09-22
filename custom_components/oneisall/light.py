"""Light platform for the feeder's status / IR illuminator light."""
from __future__ import annotations

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OneisallCoordinator
from .const import DOMAIN, DP_LIGHT
from .entity import OneisallEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OneisallCoordinator = hass.data[DOMAIN][entry.entry_id]
    if DP_LIGHT in (coordinator.data or {}):
        async_add_entities([OneisallLight(coordinator, entry)])


class OneisallLight(OneisallEntity, LightEntity):
    """On/off only - the feeder light has no brightness or colour."""

    _attr_name = "Light"
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "light")

    @property
    def is_on(self) -> bool:
        return bool(self.dps.get(DP_LIGHT, False))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_dp(DP_LIGHT, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_dp(DP_LIGHT, False)
