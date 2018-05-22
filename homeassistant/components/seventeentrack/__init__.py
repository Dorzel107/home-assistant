"""
Support for package info from 17track.net

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.seventeentrack/
"""
from logging import getLogger

from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from .config_flow import configured_tracking_numbers  # noqa
from .const import (CONF_DATA_OBJ, CONF_PACKAGES, CONF_TRACKING_NUMBER,
                    DATA_EVENTS, DATA_SUBSCRIBERS, DATA_TOPIC_UPDATE,
                    DEFAULT_REFRESH_INTERVAL, DOMAIN)

REQUIREMENTS = ['py17track==1.0.3']
_LOGGER = getLogger(__name__)


async def async_setup(hass, config):
    """Configure the platform and add the sensors."""
    from py17track import Client

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {CONF_PACKAGES: {}}

    client = SeventeenTrack(Client())
    hass.data[DOMAIN][CONF_DATA_OBJ] = client
    hass.data[DOMAIN][DATA_EVENTS] = []
    hass.data[DOMAIN][DATA_SUBSCRIBERS] = []

    def refresh_data(event_time):
        """Refresh RainMachine data."""
        _LOGGER.debug('Updating 17track.net data')
        client.update()
        async_dispatcher_send(hass, DATA_TOPIC_UPDATE)

    async_track_time_interval(hass, refresh_data, DEFAULT_REFRESH_INTERVAL)

    return True


async def async_setup_entry(hass, config_entry):
    """Create a new package via a config flow."""
    from py17track.exceptions import InvalidTrackingNumberError

    seventeentrack = hass.data[DOMAIN][CONF_DATA_OBJ]
    seventeentrack.tracking_numbers.append(
        config_entry.data[CONF_TRACKING_NUMBER])

    try:
        await hass.async_add_job(seventeentrack.update)
    except InvalidTrackingNumberError:
        _LOGGER.error('No valid tracking numbers: %s',
                      seventeentrack.tracking_numbers)

    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, 'sensor'))

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    hass.data[DOMAIN][CONF_DATA_OBJ].tracking_numbers.remove(
        config_entry.data[CONF_TRACKING_NUMBER])

    await hass.config_entries.async_forward_entry_unload(
        config_entry, 'sensor')

    dispatchers = (
        hass.data[DOMAIN][DATA_SUBSCRIBERS] + hass.data[DOMAIN][DATA_EVENTS])
    for unsub_dispatcher in dispatchers:
        unsub_dispatcher()
    hass.data[DOMAIN][DATA_EVENTS] = []
    hass.data[DOMAIN][DATA_SUBSCRIBERS] = []

    return True


class SeventeenTrack(object):
    """Define a data object to retrieve data from 17track.net."""

    def __init__(self, client, tracking_numbers=None):
        """Initialize."""
        self._client = client
        self.tracking_numbers = tracking_numbers if tracking_numbers else []
        self.packages = {}

    def update(self):
        """Update the data."""
        if not self.tracking_numbers:
            return

        data = self._client.track(*self.tracking_numbers)

        _LOGGER.debug('New data received: %s', data)

        self.packages = data
