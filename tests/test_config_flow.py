"""Tests for the config and options flow."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.components.climate import ATTR_HVAC_ACTION, HVACAction
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_NAME, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.better_thermostat_call_for_heat.const import (
    CONF_CLIMATES,
    CONF_SWITCH,
    DOMAIN,
)

from .conftest import CLIMATE_1, CLIMATE_2, SWITCH


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    """The user step creates an entry titled with the given name."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Boiler", CONF_CLIMATES: [CLIMATE_1, CLIMATE_2], CONF_SWITCH: SWITCH},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Boiler"
    assert result["options"][CONF_CLIMATES] == [CLIMATE_1, CLIMATE_2]
    assert result["options"][CONF_SWITCH] == SWITCH


async def test_options_flow_changes_watched_entities(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    switch_calls: list[tuple[str, str]],
) -> None:
    """Changing the options reloads the entry with the new entities."""
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_CLIMATES: ["climate.office"], CONF_SWITCH: "input_boolean.heat"},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert config_entry.options[CONF_CLIMATES] == ["climate.office"]
    assert config_entry.options[CONF_SWITCH] == "input_boolean.heat"

    switch_calls.clear()
    hass.states.async_set(CLIMATE_1, "heat", {ATTR_HVAC_ACTION: HVACAction.HEATING})
    await hass.async_block_till_done()
    assert switch_calls == []

    hass.states.async_set("climate.office", "heat", {ATTR_HVAC_ACTION: HVACAction.HEATING})
    await hass.async_block_till_done()
    assert switch_calls == [(SERVICE_TURN_ON, "input_boolean.heat")]
