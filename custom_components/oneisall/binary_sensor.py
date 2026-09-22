"""Binary sensors decoded from the feeder's state and fault datapoints."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OneisallCoordinator
from .const import (
    BIT_BATTERY_POWERED,
    BIT_FOOD_EMPTY,
    DOMAIN,
    DP_CHARGING,
    DP_COVER,
    DP_FAULT,
    FAULT_BITS_NOT_A_PROBLEM,
)
from .entity import OneisallEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OneisallCoordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data or {}
    entities: list[BinarySensorEntity] = []
    if DP_CHARGING in data:
        entities.append(OneisallChargingSensor(coordinator, entry))
    if DP_COVER in data:
        entities.append(OneisallLidSensor(coordinator, entry))
    if DP_FAULT in data:
        entities.append(OneisallProblemSensor(coordinator, entry))
        entities.append(OneisallHopperEmptySensor(coordinator, entry))
        entities.append(OneisallMainsPowerSensor(coordinator, entry))
    async_add_entities(entities)


class OneisallChargingSensor(OneisallEntity, BinarySensorEntity):
    """Whether the internal batteries are charging."""

    _attr_name = "Charging"
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "charging")

    @property
    def is_on(self) -> bool:
        return bool(self.dps.get(DP_CHARGING, False))


class OneisallLidSensor(OneisallEntity, BinarySensorEntity):
    """Hopper lid. The device reports the string "on" when the lid is CLOSED."""

    _attr_name = "Lid"
    _attr_device_class = BinarySensorDeviceClass.OPENING
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "lid")

    @property
    def is_on(self) -> bool:
        return self.dps.get(DP_COVER) == "off"


class OneisallProblemSensor(OneisallEntity, BinarySensorEntity):
    """Any fault bit that represents an actual malfunction.

    food_empty and battery_powered are excluded: both have their own
    dedicated sensors, and neither is a fault in its own right.
    """

    _attr_name = "Problem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "problem")

    @property
    def is_on(self) -> bool:
        value = self.dps.get(DP_FAULT)
        if not isinstance(value, int):
            return False
        return bool(value & ~FAULT_BITS_NOT_A_PROBLEM)


class OneisallHopperEmptySensor(OneisallEntity, BinarySensorEntity):
    """Out of food."""

    _attr_name = "Hopper empty"
    _attr_icon = "mdi:bowl-outline"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "hopper_empty")

    @property
    def is_on(self) -> bool:
        value = self.dps.get(DP_FAULT)
        return bool(isinstance(value, int) and value & BIT_FOOD_EMPTY)


class OneisallMainsPowerSensor(OneisallEntity, BinarySensorEntity):
    """On when running from the mains adapter rather than the batteries."""

    _attr_name = "Mains power"
    _attr_device_class = BinarySensorDeviceClass.PLUG
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: OneisallCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "mains_power")

    @property
    def is_on(self) -> bool:
        value = self.dps.get(DP_FAULT)
        return not (isinstance(value, int) and value & BIT_BATTERY_POWERED)
