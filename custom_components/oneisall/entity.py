"""Shared base entity for the Oneisall Pet Feeder integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, DOMAIN, MANUFACTURER, MODEL


class OneisallEntity(CoordinatorEntity):
    """Common device wiring so every platform reports one device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, key: str) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_DEVICE_ID])},
            name=entry.data[CONF_NAME],
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def dps(self) -> dict:
        """The most recent raw datapoint map."""
        return self.coordinator.data or {}
