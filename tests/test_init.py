"""Tests for the switch being driven by the thermostats' hvac_action."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.components.climate import ATTR_HVAC_ACTION, HVACAction
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import (
    EVENT_HOMEASSISTANT_STARTED,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.core import CoreState, HomeAssistant

from .conftest import CLIMATE_1, CLIMATE_2, SWITCH

ON = (SERVICE_TURN_ON, SWITCH)
OFF = (SERVICE_TURN_OFF, SWITCH)


def set_action(hass: HomeAssistant, entity_id: str, action: HVACAction, **attrs) -> None:
    """Set a climate entity's state with the given hvac_action."""
    hass.states.async_set(entity_id, "heat", {ATTR_HVAC_ACTION: action, **attrs})


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Set up the config entry and wait for it to settle."""
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_setup_turns_switch_off_when_nothing_heats(
    hass: HomeAssistant, config_entry: MockConfigEntry, switch_calls: list
) -> None:
    """Adding an entry syncs the switch straight away."""
    set_action(hass, CLIMATE_1, HVACAction.IDLE)
    set_action(hass, CLIMATE_2, HVACAction.IDLE)

    await setup_entry(hass, config_entry)

    assert switch_calls == [OFF]


async def test_setup_turns_switch_on_when_already_heating(
    hass: HomeAssistant, config_entry: MockConfigEntry, switch_calls: list
) -> None:
    """Adding an entry while a thermostat is heating turns the switch on."""
    set_action(hass, CLIMATE_1, HVACAction.IDLE)
    set_action(hass, CLIMATE_2, HVACAction.HEATING)

    await setup_entry(hass, config_entry)

    assert switch_calls == [ON]


async def test_switch_follows_any_thermostat_heating(
    hass: HomeAssistant, config_entry: MockConfigEntry, switch_calls: list
) -> None:
    """The switch stays on until the last heating thermostat stops."""
    set_action(hass, CLIMATE_1, HVACAction.IDLE)
    set_action(hass, CLIMATE_2, HVACAction.IDLE)
    await setup_entry(hass, config_entry)
    switch_calls.clear()

    set_action(hass, CLIMATE_1, HVACAction.HEATING)
    await hass.async_block_till_done()
    assert switch_calls == [ON]

    set_action(hass, CLIMATE_2, HVACAction.HEATING)
    await hass.async_block_till_done()
    assert switch_calls == [ON, ON]

    set_action(hass, CLIMATE_1, HVACAction.IDLE)
    await hass.async_block_till_done()
    assert switch_calls == [ON, ON, ON]

    set_action(hass, CLIMATE_2, HVACAction.IDLE)
    await hass.async_block_till_done()
    assert switch_calls == [ON, ON, ON, OFF]


async def test_other_attribute_changes_are_ignored(
    hass: HomeAssistant, config_entry: MockConfigEntry, switch_calls: list
) -> None:
    """A temperature update with the same hvac_action does not touch the switch."""
    set_action(hass, CLIMATE_1, HVACAction.HEATING, current_temperature=19.0)
    await setup_entry(hass, config_entry)
    switch_calls.clear()

    set_action(hass, CLIMATE_1, HVACAction.HEATING, current_temperature=19.5)
    await hass.async_block_till_done()

    assert switch_calls == []


async def test_unavailable_thermostat_counts_as_not_heating(
    hass: HomeAssistant, config_entry: MockConfigEntry, switch_calls: list
) -> None:
    """A heating thermostat that drops out turns the switch off."""
    set_action(hass, CLIMATE_1, HVACAction.HEATING)
    await setup_entry(hass, config_entry)
    switch_calls.clear()

    hass.states.async_set(CLIMATE_1, STATE_UNAVAILABLE)
    await hass.async_block_till_done()

    assert switch_calls == [OFF]


async def test_missing_thermostats_count_as_not_heating(
    hass: HomeAssistant, config_entry: MockConfigEntry, switch_calls: list
) -> None:
    """Thermostats with no state at all do not turn the switch on."""
    await setup_entry(hass, config_entry)

    assert switch_calls == [OFF]


async def test_waits_for_home_assistant_to_start(
    hass: HomeAssistant, config_entry: MockConfigEntry, switch_calls: list
) -> None:
    """During startup the switch is left alone, then synced once when started."""
    hass.set_state(CoreState.not_running)
    await setup_entry(hass, config_entry)

    set_action(hass, CLIMATE_1, HVACAction.HEATING)
    await hass.async_block_till_done()
    assert switch_calls == []

    hass.set_state(CoreState.running)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await hass.async_block_till_done()
    assert switch_calls == [ON]


async def test_unload_stops_driving_the_switch(
    hass: HomeAssistant, config_entry: MockConfigEntry, switch_calls: list
) -> None:
    """After unloading, thermostat changes no longer reach the switch."""
    await setup_entry(hass, config_entry)
    switch_calls.clear()

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED

    set_action(hass, CLIMATE_1, HVACAction.HEATING)
    await hass.async_block_till_done()

    assert switch_calls == []
