"""Sensor platform: status, battery, faults, last feed, and raw DPS."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OneisallCoordinator
from .const import (
    DOMAIN,
    DP_BATTERY,
    DP_FAULT,
    DP_FEED_REPORT,
    DP_STATUS,
    FAULT_BITS,
    STATUS_MAP,
)
from .entity import OneisallEntity


def decode_faults(value) -> list[str]:
    """Split the DP13 bitfield into the list of conditions currently set."""
    if not isinstance(value, int) or value <= 0:
        return []
    return [name for bit, name in FAULT_BITS.items() if value & bit]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OneisallCoordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data or {}
    entities: list[SensorEntity] = [OneisallRawDpsSensor(coordinator, entry)]
    if DP_STATUS in data:
        entities.append(OneisallStatusSensor(coordinator, entry))
    if DP_BATTERY in data:
        entities.append(OneisallBatterySensor(coordinator, entry))
    if DP_FAULT in data:
        entities.append(OneisallFaultSensor(coordinator, entry))
    if DP_FEED_REPORT in data:
        entities.append(OneisallLastFeedSensor(coordinator, entry))
    async_add_entities(entities)


class OneisallStatusSensor(OneisallEntity, SensorEntity):
    """What the feeder is doing right now."""

    _attr_name = "Status"
    _attr_icon = "mdi:information-outline"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = sorted(set(STATUS_MAP.values()))

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "status")

    @property
    def native_value(self) -> str | None:
        return STATUS_MAP.get(self.dps.get(DP_STATUS))


class OneisallBatterySensor(OneisallEntity, SensorEntity):
    """Battery charge."""

    _attr_name = "Battery"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "battery")

    @property
    def native_value(self) -> int | None:
        value = self.dps.get(DP_BATTERY)
        return int(value) if isinstance(value, (int, float)) else None


class OneisallFaultSensor(OneisallEntity, SensorEntity):
    """Human-readable fault state, with every active condition as an attribute."""

    _attr_name = "Fault"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "fault")

    @property
    def native_value(self) -> str:
        faults = decode_faults(self.dps.get(DP_FAULT))
        return ", ".join(faults) if faults else "ok"

    @property
    def extra_state_attributes(self) -> dict:
        raw = self.dps.get(DP_FAULT)
        return {"raw": raw, "active": decode_faults(raw)}


class OneisallLastFeedSensor(OneisallEntity, SensorEntity):
    """Portions dispensed by the most recent feed."""

    _attr_name = "Last feed"
    _attr_icon = "mdi:history"
    _attr_native_unit_of_measurement = "portions"

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "last_feed")

    @property
    def native_value(self) -> int | None:
        value = self.dps.get(DP_FEED_REPORT)
        return int(value) if isinstance(value, (int, float)) else None


class OneisallRawDpsSensor(OneisallEntity, SensorEntity):
    """Shows the count of known DPS, with the full raw map as attributes.

    This is the tool for extending the integration: watch this entity's
    attributes while changing settings in the Oneisall app, note which DP
    number moves and what values it takes, then add a proper entity for it.
    """

    _attr_name = "Raw DPS"
    _attr_icon = "mdi:code-braces"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "raw_dps")

    @property
    def native_value(self) -> int:
        return len(self.dps)

    @property
    def extra_state_attributes(self) -> dict:
        return dict(self.dps)
