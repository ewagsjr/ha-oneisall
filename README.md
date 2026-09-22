# ha-oneisall

Local Home Assistant integration for the **Oneisall PF-002 Pro** Wi-Fi pet feeder, over the Tuya local protocol. No cloud, no polling of Tuya's servers — Home Assistant talks straight to the feeder on your LAN.

Built in the same shape as [ha-fancyled](https://github.com/ewagsjr/ha-fancyled): a `tinytuya` coordinator, one entity per datapoint, and a raw-DPS diagnostic sensor plus a `set_raw_dp` service so you can map anything this integration doesn't model yet.

> [!IMPORTANT]
> **Status: untested against hardware.** The datapoint map is taken from a published, working device config (see [Datapoints](#datapoints)), but no one has yet run this code against a real feeder. Treat the first setup as a bring-up: install it, watch the **Raw DPS** sensor, and open an issue if a datapoint doesn't behave as documented.

## Should you use this instead of tuya-local?

Probably not, and it's worth being straight about that.

[`make-all/tuya-local`](https://github.com/make-all/tuya-local) already supports this exact feeder (`oneisall_pfd002pro_petfeeder.yaml`) as one of a thousand device configs, and it is actively maintained by people with the hardware. If you just want the feeder working in Home Assistant, install that.

This repo exists for the case where you'd rather have a small, self-contained component you fully control — one file per platform, no YAML device-config engine in between, and a documented DP map you can extend yourself.

## Installation

### HACS (custom repository)

1. HACS → **Integrations** → ⋮ → **Custom repositories**
2. Add `https://github.com/ewagsjr/ha-oneisall`, category **Integration**
3. Install **Oneisall Pet Feeder**, then restart Home Assistant

### Manual

Copy `custom_components/oneisall/` into your Home Assistant `config/custom_components/` directory and restart.

## Configuration

**Settings → Devices & Services → Add Integration → Oneisall Pet Feeder**

You'll need four things:

| Field | Where it comes from |
| --- | --- |
| IP address | Your router's client list. Give the feeder a DHCP reservation — a local Tuya session is bound to the address. |
| Device ID | Tuya IoT Cloud developer portal |
| Local key | Tuya IoT Cloud developer portal |
| Protocol version | `3.4` for most current firmware; try `3.3` then `3.5` if the connection test fails |

### Getting the device ID and local key

These are not visible in the Oneisall app. The standard route:

1. Create a free account at [iot.tuya.com](https://iot.tuya.com) and start a Cloud project (Smart Home, your region).
2. Under **Devices → Link App Account**, link the app your feeder is paired with.
3. The feeder appears in the device list; open it and copy the **Device ID** and **Local Key**.

The `python -m tinytuya wizard` helper automates most of this once the cloud project exists.

> The local key rotates whenever the device is re-paired in the app. If the integration suddenly stops connecting, re-read the key.

## Entities

| Entity | Type | Datapoint |
| --- | --- | --- |
| Quick feed | button | 2 |
| Manual feed | number (1–60 portions) | 3 |
| Status | sensor (standby / feeding / complete) | 4 |
| Battery | sensor (%) | 10 |
| Charging | binary sensor | 11 |
| Lid | binary sensor (opening) | 12 |
| Problem | binary sensor | 13 |
| Hopper empty | binary sensor | 13 (bit 4) |
| Mains power | binary sensor | 13 (bit 64) |
| Fault | sensor (diagnostic) | 13 |
| Last feed | sensor (portions) | 14 |
| Light | light (on/off) | 17 |
| Slow feed | switch | 23 |
| Weight calibration | switch | 26 |
| Power mode | select | 101 |
| Factory reset | button (disabled by default) | 24 |
| Raw DPS | sensor (diagnostic) | all |

Entities are only created for datapoints the feeder actually reports, so a model with a smaller feature set simply gets fewer entities rather than a row of `unavailable`.

## Datapoints

The DP map in [`const.py`](custom_components/oneisall/const.py) comes from the device config published in `make-all/tuya-local` for Tuya product id `ebdq15yidek4phti` (Oneisall PF-002 Pro IR).

DP13 is a **bitfield**, so several conditions can be true at once. This integration decodes it bit by bit:

| Bit | Meaning |
| --- | --- |
| 1 | Jammed |
| 2 | Food low |
| 4 | Food empty |
| 8 | Desiccant low |
| 16 | Battery low |
| 32 | Stuck |
| 64 | Running on battery |

The generic **Problem** sensor deliberately ignores bits 4 and 64 — food empty has its own sensor, and running on battery is a normal state during a power cut, not a malfunction.

## Extending it

Anything not in the table above shows up in the **Raw DPS** diagnostic sensor's attributes. To identify an unknown datapoint:

1. Watch `sensor.<name>_raw_dps` attributes in Developer Tools → States.
2. Change the setting in the Oneisall app and note which DP number moves and what values it takes.
3. Write it back with the service to confirm:

```yaml
action: oneisall.set_raw_dp
data:
  entry_id: <your config entry id>
  dp: "102"
  value: true
```

4. Add a constant to `const.py` and an entity to the matching platform file.

## Licence

MIT
