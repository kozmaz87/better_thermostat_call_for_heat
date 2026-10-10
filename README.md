# Better Thermostat Call For Heat

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![Release](https://img.shields.io/github/v/release/kozmaz87/better_thermostat_call_for_heat)](https://github.com/kozmaz87/better_thermostat_call_for_heat/releases)
[![Validate](https://github.com/kozmaz87/better_thermostat_call_for_heat/actions/workflows/validate.yml/badge.svg)](https://github.com/kozmaz87/better_thermostat_call_for_heat/actions/workflows/validate.yml)

A Home Assistant custom integration that drives a master switch (e.g. a boiler relay) from a group of
thermostats: the switch is turned **on** while any selected climate entity reports `hvac_action: heating`,
and **off** when none of them do.

It replaces a hand-written automation with a form: pick the thermostats, pick the switch, done.

## Installation (HACS)

[![Open your Home Assistant instance and open this repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kozmaz87&repository=better_thermostat_call_for_heat&category=integration)

Click the button above, then **Download**, and restart Home Assistant. Or add it by hand:

1. HACS → three-dot menu → **Custom repositories**.
2. Add `https://github.com/kozmaz87/better_thermostat_call_for_heat` with type **Integration**.
3. Install **Better Thermostat Call For Heat** and restart Home Assistant.

Manual install: copy `custom_components/better_thermostat_call_for_heat` into your Home Assistant
`config/custom_components` folder and restart.

## Setup

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=better_thermostat_call_for_heat)

Click the button above, or go to
**Settings → Devices & services → Add integration → Better Thermostat Call For Heat**, then fill in:

| Field | Meaning |
|---|---|
| Name | Label for this master switch |
| Thermostats | Climate entities whose `hvac_action` is watched |
| Master switch | The `switch` or `input_boolean` to turn on and off |

Add the integration again for each additional heating zone. Use **Configure** on an entry to change the
thermostats or the switch later.

## Behaviour

- The switch is re-evaluated whenever a watched thermostat's `hvac_action` changes, when Home Assistant has
  finished starting, and when an entry is added or reconfigured.
- Any `hvac_action` other than `heating` (`idle`, `off`, or an unavailable thermostat) counts as not heating.
- Manual changes to the switch are not reverted until the next `hvac_action` change.
