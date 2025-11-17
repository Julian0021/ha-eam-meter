"""The EAM Meter integration."""

from __future__ import annotations

import logging
import voluptuous as vol
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import Platform, CONF_USERNAME, CONF_PASSWORD
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, MAIN_URL, CONF_ENTITY_ID
from .eam_api import get_session_key, get_selected_read, post_readout

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

SERVICE_SUBMIT_READOUT = "submit_readout"

SERVICE_SUBMIT_SCHEMA = vol.Schema({})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EAM Meter from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id]["config"] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def async_submit_readout(call: ServiceCall) -> None:
        """Handle the submit_readout service call."""
        # Get the entity_id from config
        entity_id = entry.data.get(CONF_ENTITY_ID)

        if not entity_id:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="no_entity_configured"
            )

        state = hass.states.get(entity_id)

        if not state:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="entity_not_found",
                translation_placeholders={"entity_id": entity_id}
            )

        try:
            readout_value = round(float(state.state))
        except (ValueError, TypeError) as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="invalid_readout_value",
                translation_placeholders={"value": str(state.state)}
            ) from err

        if readout_value <= 0:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="readout_must_be_positive"
            )

        # Check if readout value is greater than last readout
        coordinator = hass.data[DOMAIN][entry.entry_id].get("coordinator")
        if not coordinator:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="coordinator_not_found"
            )
        
        last_readout = coordinator.data.get("value")
        if last_readout and readout_value <= last_readout:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="readout_too_low",
                translation_placeholders={
                    "new_value": str(readout_value),
                    "last_value": str(last_readout)
                }
            )
        
        # Check if there was already a submission in the current month
        last_date_str = coordinator.data.get("date")
        if last_date_str:
            try:
                last_date = datetime.strptime(last_date_str, "%d.%m.%Y")
                current_date = datetime.now()
                
                if last_date.year == current_date.year and last_date.month == current_date.month:
                    raise HomeAssistantError(
                        translation_domain=DOMAIN,
                        translation_key="already_submitted_this_month",
                        translation_placeholders={"date": last_date_str}
                    )
            except ValueError:
                _LOGGER.warning("Could not parse last submission date: %s", last_date_str)
            
        # Get credentials from config
        username = entry.data[CONF_USERNAME]
        password = entry.data[CONF_PASSWORD]

        try:
            # Step 1: Get session key
            _LOGGER.info("Getting session key for EAM meter")
            session_key = await hass.async_add_executor_job(
                get_session_key, MAIN_URL, username, password
            )

            # Step 2: Get metadata
            _LOGGER.info("Getting metadata for EAM meter")
            selected_read = await hass.async_add_executor_job(
                get_selected_read, session_key, MAIN_URL
            )

            # Step 3: Post readout
            _LOGGER.info("Posting readout: %s kWh", readout_value)
            success = await hass.async_add_executor_job(
                post_readout, session_key, selected_read, readout_value, MAIN_URL
            )

            if success:
                _LOGGER.info("Successfully posted readout: %s kWh", readout_value)

                # Step 4: Refresh the last readout sensor
                coordinator = hass.data[DOMAIN][entry.entry_id].get("coordinator")
                if coordinator:
                    _LOGGER.debug("Refreshing last readout sensor")
                    await coordinator.async_request_refresh()
            else:
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="post_failed"
                )

        except HomeAssistantError:
            raise
        except Exception as err:
            _LOGGER.error("Error posting readout: %s", err)
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="submit_failed",
                translation_placeholders={"error": str(err)}
            ) from err

    # Register the service
    hass.services.async_register(
        DOMAIN,
        SERVICE_SUBMIT_READOUT,
        async_submit_readout,
        schema=SERVICE_SUBMIT_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        # Remove service if no more config entries
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_SUBMIT_READOUT)
    return unload_ok
