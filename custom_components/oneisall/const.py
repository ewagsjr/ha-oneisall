"""Constants for the Oneisall Pet Feeder integration."""

DOMAIN = "oneisall"

CONF_DEVICE_ID = "device_id"
CONF_LOCAL_KEY = "local_key"
CONF_PROTOCOL_VERSION = "protocol_version"

DEFAULT_PROTOCOL_VERSION = "3.4"
DEFAULT_NAME = "Cat Feeder"
DEFAULT_PORT = 6668

UPDATE_INTERVAL_SECONDS = 30

MANUFACTURER = "Oneisall"
MODEL = "PF-002 Pro"

# --- DPS map for the Oneisall PF-002 Pro IR pet feeder
# (Tuya product id ebdq15yidek4phti).
#
# Taken from the device config published in make-all/tuya-local:
#   custom_components/tuya_local/devices/oneisall_pfd002pro_petfeeder.yaml
# That project is the authoritative source for this hardware; this
# integration exists to give the feeder a standalone, dependency-free
# component in the same shape as ha-fancyled.
#
# If your unit reports datapoints not listed here, watch the "Raw DPS"
# diagnostic sensor while changing settings in the Oneisall app, then
# extend the platforms below.
DP_MEAL_PLAN = "1"        # base64 string, encoded feeding schedule
DP_QUICK_FEED = "2"       # bool, write-only trigger for a single portion
DP_MANUAL_FEED = "3"      # int 1-60, portions to dispense now
DP_STATUS = "4"           # enum: standby / feeding / done
DP_BATTERY = "10"         # int 0-100 (%)
DP_CHARGING = "11"        # bool
DP_COVER = "12"           # enum on/off - "on" means the hopper lid is CLOSED
DP_FAULT = "13"           # bitfield, see FAULT_BITS
DP_FEED_REPORT = "14"     # int, portions actually dispensed (feed event)
DP_LIGHT = "17"           # bool, IR / status light
DP_SLOW_FEED = "23"       # bool
DP_FACTORY_RESET = "24"   # bool, write-only
DP_WEIGHT_CALIBRATION = "26"  # bool
DP_POWER_MODE = "101"     # enum: strong_power / battery_power

STATUS_MAP = {
    "standby": "standby",
    "feeding": "feeding",
    "done": "feeding_complete",
}

# DP13 is a bitfield - several conditions can be set at once, so it must be
# decoded bit by bit rather than matched against whole values.
FAULT_BITS = {
    1: "jammed",
    2: "food_low",
    4: "food_empty",
    8: "desiccant_low",
    16: "battery_low",
    32: "stuck",
    64: "battery_powered",
}

BIT_FOOD_EMPTY = 4
BIT_BATTERY_POWERED = 64

# Bits that describe a state rather than a fault, so they must not raise the
# generic "problem" sensor: food_empty has its own sensor, and running on
# battery is normal during a power cut.
FAULT_BITS_NOT_A_PROBLEM = BIT_FOOD_EMPTY | BIT_BATTERY_POWERED

POWER_MODES = {
    "strong_power": "Full power",
    "battery_power": "Battery saver",
}
