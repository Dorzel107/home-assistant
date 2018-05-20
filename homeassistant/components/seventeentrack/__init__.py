"""
Support for package info from 17track.net

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.seventeentrack/
"""
from logging import getLogger

from homeassistant.util import slugify

from .const import (CONF_DATA_OBJ, CONF_TRACKING_NUMBER, CONF_PACKAGES, DOMAIN)
from .package import PackageSensor, SeventeenTrackData

REQUIREMENTS = ['py17track==1.0.2']
_LOGGER = getLogger(__name__)


async def async_setup(hass, config):
    """Configure the platform and add the sensors."""
    from py17track import Client

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {CONF_PACKAGES: {}}

    hass.data[DOMAIN][CONF_DATA_OBJ] = SeventeenTrackData(Client())

    return True


async def async_setup_entry(hass, config_entry):
    """Create a new package via a config flow."""
    entry = config_entry.data
    key = slugify(entry[CONF_TRACKING_NUMBER])
    data = hass.data[DOMAIN][CONF_DATA_OBJ]

    data.tracking_numbers.append([entry[CONF_TRACKING_NUMBER]])
    package = PackageSensor(data, entry[CONF_TRACKING_NUMBER])
    hass.async_add_job(package.async_update_ha_state())
    hass.data[DOMAIN][CONF_PACKAGES][key] = package
    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    packages = hass.data[DOMAIN][CONF_PACKAGES]
    key = slugify(config_entry.data[CONF_TRACKING_NUMBER])
    data = hass.data[DOMAIN][CONF_DATA_OBJ]

    data.tracking_numbers.remove(config_entry.data[CONF_TRACKING_NUMBER])
    package = packages.pop(key)
    await package.async_remove()
    return True
