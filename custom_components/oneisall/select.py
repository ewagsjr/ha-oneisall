"""Select platform: power mode."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OneisallCoordinator
from .const import DOMAIN, DP_POWER_MODE, POWER_MODES
from .entity import OneisallEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OneisallCoordinator = hass.data[DOMAIN][entry.entry_id]
    if DP_POWER_MODE in (coordinator.data or {}):
        async_add_entities([OneisallPowerModeSelect(coordinator, entry)])


class OneisallPowerModeSelect(OneisallEntity, SelectEntity):
    """Full power vs battery saver."""

    _attr_name = "Power mode"
    _attr_icon = "mdi:signal"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(POWER_MODES.values())

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "power_mode")

    @property
    def current_option(self) -> str | None:
        return POWER_MODES.get(self.dps.get(DP_POWER_MODE))

    async def async_select_option(self, option: str) -> None:
        raw = next((k for k, v in POWER_MODES.items() if v == option), None)
        if raw is not None:
            await self.coordinator.async_set_dp(DP_POWER_MODE, raw)
