"""Config flow for the Better Thermostat Call For Heat integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
)

from .const import CONF_CLIMATES, CONF_SWITCH, DOMAIN

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLIMATES): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="climate", multiple=True)
        ),
        vol.Required(CONF_SWITCH): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["switch", "input_boolean"])
        ),
    }
)

CONFIG_SCHEMA = vol.Schema({vol.Required(CONF_NAME): selector.TextSelector()}).extend(
    OPTIONS_SCHEMA.schema
)

CONFIG_FLOW = {"user": SchemaFlowFormStep(CONFIG_SCHEMA)}
OPTIONS_FLOW = {"init": SchemaFlowFormStep(OPTIONS_SCHEMA)}


class CallForHeatConfigFlow(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle the config and options flow for a master switch."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return the config entry title."""
        return options[CONF_NAME]
