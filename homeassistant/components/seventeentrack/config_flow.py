"""Config flow to configure the 17track component."""
import voluptuous as vol

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.util import slugify

from .const import CONF_TRACKING_NUMBER, DOMAIN

CONF_SETUP_METHOD = 'setup_method'


@callback
def configured_entries(hass):
    """Return a set of the configured hosts."""
    return set(
        slugify(
            entry.data.get(CONF_EMAIL) or entry.data[CONF_TRACKING_NUMBER])
        for entry in hass.config_entries.async_entries(DOMAIN))


@config_entries.HANDLERS.register(DOMAIN)
class SeventeenTrackFlowHandler(data_entry_flow.FlowHandler):
    """Define a 17track config flow."""

    VERSION = 1

    def __init__(self):
        """Initialize."""
        pass

    async def async_step_init(self, user_input=None):
        """Handle a flow start."""
        errors = {}

        if user_input is not None:
            if user_input[CONF_SETUP_METHOD] == 'Ad Hoc':
                return await self.async_step_ad_hoc()
            return await self.async_step_account()

        return self.async_show_form(
            step_id='init',
            data_schema=vol.Schema({
                vol.Required(CONF_SETUP_METHOD):
                vol.In(['Account', 'Ad Hoc']),
            }),
            errors=errors)

    async def async_step_account(self, user_input=None):
        """Handle an ad hoc package addition."""
        errors = {}

        if user_input is not None:
            key = slugify(user_input[CONF_EMAIL])
            if key not in configured_entries(self.hass):
                return self.async_create_entry(
                    title=user_input[CONF_EMAIL],
                    data=user_input,
                )
            errors['base'] = 'account_exists'

        return self.async_show_form(
            step_id='account',
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )

    async def async_step_ad_hoc(self, user_input=None):
        """Handle an ad hoc package addition."""
        errors = {}

        if user_input is not None:
            key = slugify(user_input[CONF_TRACKING_NUMBER])
            if key not in configured_entries(self.hass):
                return self.async_create_entry(
                    title=user_input[CONF_TRACKING_NUMBER],
                    data=user_input,
                )
            errors['base'] = 'tracking_number_exists'

        return self.async_show_form(
            step_id='ad_hoc',
            data_schema=vol.Schema({
                vol.Required(CONF_TRACKING_NUMBER): str,
            }),
            errors=errors,
        )
