"""Button platform: quick feed, and a hidden factory reset."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OneisallCoordinator
from .const import DOMAIN, DP_FACTORY_RESET, DP_QUICK_FEED
from .entity import OneisallEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OneisallCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            OneisallQuickFeedButton(coordinator, entry),
            OneisallFactoryResetButton(coordinator, entry),
        ]
    )


class OneisallQuickFeedButton(OneisallEntity, ButtonEntity):
    """Dispense a single portion immediately."""

    _attr_name = "Quick feed"
    _attr_icon = "mdi:bowl-mix"

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "quick_feed")

    async def async_press(self) -> None:
        await self.coordinator.async_set_dp(DP_QUICK_FEED, True)


class OneisallFactoryResetButton(OneisallEntity, ButtonEntity):
    """Factory reset. Disabled by default - this wipes the feeder's pairing."""

    _attr_name = "Factory reset"
    _attr_icon = "mdi:restore-alert"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "factory_reset")

    async def async_press(self) -> None:
        await self.coordinator.async_set_dp(DP_FACTORY_RESET, True)
