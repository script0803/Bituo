import asyncio
import logging
import requests
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN, CONF_HOST_IP

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BUTTON, Platform.SWITCH]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bituo integration from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    host_ip = entry.data[CONF_HOST_IP]
    _LOGGER.info("Setting up Bituo integration for %s", host_ip)

    # Initialize the data dictionary for this entry
    hass.data[DOMAIN][entry.entry_id] = {}

    # Fetch device data to get model id and verify connection
    try:
        response = await hass.async_add_executor_job(
            requests.get, f"http://{host_ip}/data"
        )
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        model_id = data.get("ProductModel") or data.get("productModel", "Unknown Model")
    except requests.exceptions.RequestException as e:
        _LOGGER.error("Error fetching device data from %s: %s", host_ip, e)
        raise ConfigEntryNotReady from e

    # Update the entry title to be "modelid - ip"
    hass.config_entries.async_update_entry(
        entry, title=f"{model_id} - {host_ip}"
    )

    # Forward the setup to the sensor and control platforms
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except ConfigEntryNotReady as e:
        _LOGGER.error("Error setting up platforms for Bituo: %s", e)
        raise ConfigEntryNotReady from e

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Bituo config entry."""
    _LOGGER.info("Unloading Bituo integration for %s", entry.data[CONF_HOST_IP])

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        _LOGGER.info("Successfully unloaded Bituo integration for %s", entry.data[CONF_HOST_IP])
        if DOMAIN in hass.data:
            hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    _LOGGER.info("Removing Bituo integration for %s", entry.data[CONF_HOST_IP])

# by Script0803