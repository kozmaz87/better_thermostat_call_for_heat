# Better Thermostat Call For Heat

A Home Assistant custom integration that drives a master switch (e.g. a boiler relay) from a group of
thermostats: the switch is turned **on** while any selected climate entity reports `hvac_action: heating`,
and **off** when none of them do.

It replaces a hand-written automation with a form: pick the thermostats, pick the switch, done.

## Installation (HACS)

1. HACS → three-dot menu → **Custom repositories**.
2. Add this repository's URL with type **Integration**.
3. Install **Better Thermostat Call For Heat** and restart Home Assistant.

Manual install: copy `custom_components/better_thermostat_call_for_heat` into your Home Assistant
`config/custom_components` folder and restart.

## Setup

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
