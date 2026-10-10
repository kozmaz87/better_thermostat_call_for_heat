"""Better Thermostat Call For Heat.

Keeps a master switch (e.g. a boiler relay) on while any of the selected
climate entities reports an hvac_action of 'heating', and off otherwise.
"""

from __future__ import annotations

import logging

from homeassistant.components.climate import ATTR_HVAC_ACTION, HVACAction
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import (
    DOMAIN as HOMEASSISTANT_DOMAIN,
    Event,
    EventStateChangedData,
    HomeAssistant,
    State,
    callback,
)
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.start import async_at_started

from .const import CONF_CLIMATES, CONF_SWITCH

_LOGGER = logging.getLogger(__name__)


def _hvac_action(state: State | None) -> str | None:
    """Return the hvac_action of a climate state, if it has one."""
    return state.attributes.get(ATTR_HVAC_ACTION) if state else None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a master switch from a config entry."""
    climates: list[str] = entry.options[CONF_CLIMATES]
    switch: str = entry.options[CONF_SWITCH]

    @callback
    def sync_switch(_hass: HomeAssistant | None = None) -> None:
        """Turn the master switch on if any climate is heating, else off."""
        any_heating = any(
            _hvac_action(hass.states.get(entity_id)) == HVACAction.HEATING
            for entity_id in climates
        )
        service = SERVICE_TURN_ON if any_heating else SERVICE_TURN_OFF
        _LOGGER.debug("%s: any_heating=%s, calling %s on %s", entry.title, any_heating, service, switch)
        hass.async_create_task(
            hass.services.async_call(HOMEASSISTANT_DOMAIN, service, {ATTR_ENTITY_ID: switch})
        )

    @callback
    def climate_changed(event: Event[EventStateChangedData]) -> None:
        """React to hvac_action changes only, not every temperature update."""
        # During startup the climates load one by one; wait for the full picture.
        if not hass.is_running:
            return
        if _hvac_action(event.data["old_state"]) != _hvac_action(event.data["new_state"]):
            sync_switch()

    entry.async_on_unload(async_track_state_change_event(hass, climates, climate_changed))
    # Runs immediately if Home Assistant is already running (entry added or reloaded).
    entry.async_on_unload(async_at_started(hass, sync_switch))
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
