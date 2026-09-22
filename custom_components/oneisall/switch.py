"""Switch platform: slow feed and weight calibration."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OneisallCoordinator
from .const import DOMAIN, DP_SLOW_FEED, DP_WEIGHT_CALIBRATION
from .entity import OneisallEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OneisallCoordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data or {}
    entities: list[SwitchEntity] = []
    if DP_SLOW_FEED in data:
        entities.append(OneisallDpSwitch(
            coordinator, entry, "slow_feed", "Slow feed", "mdi:tortoise", DP_SLOW_FEED, None
        ))
    if DP_WEIGHT_CALIBRATION in data:
        entities.append(OneisallDpSwitch(
            coordinator, entry, "weight_calibration", "Weight calibration",
            "mdi:scale-balance", DP_WEIGHT_CALIBRATION, EntityCategory.CONFIG,
        ))
    async_add_entities(entities)


class OneisallDpSwitch(OneisallEntity, SwitchEntity):
    """A plain boolean datapoint exposed as a switch."""

    def __init__(
        self,
        coordinator: OneisallCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
        dp: str,
        category: EntityCategory | None,
    ) -> None:
        super().__init__(coordinator, entry, key)
        self._dp = dp
        self._attr_name = name
        self._attr_icon = icon
        self._attr_entity_category = category

    @property
    def is_on(self) -> bool:
        return bool(self.dps.get(self._dp, False))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_dp(self._dp, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_dp(self._dp, False)
