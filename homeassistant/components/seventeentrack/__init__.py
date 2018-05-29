"""
Support for package info from 17track.net

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.seventeentrack/
"""
from logging import getLogger

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from .config_flow import configured_entries  # noqa
from .const import (
    CONF_TRACKING_NUMBER, DATA_OBJ, DATA_SUBSCRIBERS, DATA_TOPIC_UPDATE,
    DEFAULT_REFRESH_INTERVAL, DOMAIN)

REQUIREMENTS = ['py17track==1.1.3']
_LOGGER = getLogger(__name__)


async def async_setup(hass, config):
    """Configure the platform and add the sensors."""
    from py17track import Client

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    client = SeventeenTrack(Client())
    hass.data[DOMAIN][DATA_OBJ] = client
    hass.data[DOMAIN][DATA_SUBSCRIBERS] = {}

    def refresh_data(event_time):
        """Refresh RainMachine data."""
        _LOGGER.debug('Updating 17track.net data')
        client.update()
        async_dispatcher_send(hass, DATA_TOPIC_UPDATE)

    async_track_time_interval(hass, refresh_data, DEFAULT_REFRESH_INTERVAL)

    return True


async def async_setup_entry(hass, config_entry):
    """Create a new package via a config flow."""
    seventeentrack = hass.data[DOMAIN][DATA_OBJ]

    if config_entry.data.get(CONF_TRACKING_NUMBER):
        # 1. Ad Hoc Flow
        seventeentrack.tracking_numbers.append(
            config_entry.data[CONF_TRACKING_NUMBER])
    else:
        # 2. Account Flow
        await hass.async_add_job(seventeentrack.login,
                                 config_entry.data[CONF_EMAIL],
                                 config_entry.data[CONF_PASSWORD])

    await hass.async_add_job(seventeentrack.update)

    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, 'sensor'))

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    if config_entry.data.get(CONF_TRACKING_NUMBER):
        # 1. Ad Hoc Flow
        tracking_number = config_entry.data[CONF_TRACKING_NUMBER]

        unsub_dispatcher = hass.data[DOMAIN][DATA_SUBSCRIBERS].pop(
            tracking_number)
        unsub_dispatcher()

        hass.data[DOMAIN][DATA_OBJ].tracking_numbers.remove(
            tracking_number)
    else:
        # 2. Account Flow
        for package in hass.data[DOMAIN][DATA_OBJ].account_packages:
            unsub_dispatcher = hass.data[DOMAIN][DATA_SUBSCRIBERS].pop(
                package.tracking_number)
            unsub_dispatcher()

        hass.data[DOMAIN][DATA_OBJ].logout()

    await hass.config_entries.async_forward_entry_unload(
        config_entry, 'sensor')

    return True


class SeventeenTrack(object):
    """Define a data object to retrieve data from 17track.net."""

    def __init__(self, client):
        """Initialize."""
        self._authenticated = False
        self._client = client
        self.account_packages = []
        self.ad_hoc_packages = []
        self.tracking_numbers = []

    def login(self, email, password):
        """Authenticate the object with an email and password."""
        from py17track.exceptions import UnauthenticatedError

        try:
            self._client.profile.login(email, password)
            self._authenticated = True
        except UnauthenticatedError:
            _LOGGER.error('Invalid username/password')

    def logout(self):
        """Log out of the 17track.net session."""
        self._client.profile.logout()
        self._authenticated = False
        self.account_packages = []

    def update(self):
        """Update appropriate data."""
        if self._authenticated:
            self.update_account()
        if self.tracking_numbers:
            self.update_ad_hoc()

    def update_account(self):
        """Update account data."""
        self.account_packages = self._client.profile.packages()

        _LOGGER.debug('New account data received: %s', self.account_packages)

    def update_ad_hoc(self):
        """Update ad hoc data."""
        self.ad_hoc_packages = self._client.track.find(*self.tracking_numbers)

        _LOGGER.debug('New ad hoc data received: %s', self.ad_hoc_packages)

        if not self.ad_hoc_packages:
            _LOGGER.warning('No valid tracking numbers')
