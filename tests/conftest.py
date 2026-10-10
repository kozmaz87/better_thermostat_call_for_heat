"""Fixtures for the Better Thermostat Call For Heat tests."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import (
    DOMAIN as HOMEASSISTANT_DOMAIN,
    HomeAssistant,
    ServiceCall,
    callback,
)

from custom_components.better_thermostat_call_for_heat.const import (
    CONF_CLIMATES,
    CONF_SWITCH,
    DOMAIN,
)

CLIMATE_1 = "climate.living_room"
CLIMATE_2 = "climate.bedroom"
SWITCH = "switch.boiler"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Let Home Assistant load the integration from custom_components."""


@pytest.fixture(autouse=True)
def switch_calls(hass: HomeAssistant) -> list[tuple[str, str]]:
    """Record homeassistant.turn_on/turn_off calls as (service, entity_id)."""
    calls: list[tuple[str, str]] = []

    @callback
    def record(call: ServiceCall) -> None:
        calls.append((call.service, call.data[ATTR_ENTITY_ID]))

    for service in (SERVICE_TURN_ON, SERVICE_TURN_OFF):
        hass.services.async_register(HOMEASSISTANT_DOMAIN, service, record)
    return calls


@pytest.fixture
def config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return a config entry watching two thermostats, not yet set up."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Boiler",
        options={CONF_CLIMATES: [CLIMATE_1, CLIMATE_2], CONF_SWITCH: SWITCH},
    )
    entry.add_to_hass(hass)
    return entry
