"""Number platform: manual feed size in portions."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OneisallCoordinator
from .const import DOMAIN, DP_MANUAL_FEED
from .entity import OneisallEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OneisallCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OneisallManualFeedNumber(coordinator, entry)])


class OneisallManualFeedNumber(OneisallEntity, NumberEntity):
    """Portions to dispense. Writing this value triggers the feed."""

    _attr_name = "Manual feed"
    _attr_icon = "mdi:food-drumstick"
    _attr_native_min_value = 1
    _attr_native_max_value = 60
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "portions"

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "manual_feed")

    @property
    def native_value(self) -> float | None:
        value = self.dps.get(DP_MANUAL_FEED)
        return float(value) if isinstance(value, (int, float)) else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_dp(DP_MANUAL_FEED, int(value))
