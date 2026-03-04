"""Config flow for Spire Energy integration."""
from __future__ import annotations

import asyncio
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SpireClient, SpireApiError, SpireAuthError
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_ACCOUNT_ID,
    CONF_SA_ID,
    HTTP_TIMEOUT_SECONDS,
)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_ACCOUNT_ID): str,
        vol.Required(CONF_SA_ID): str,
    }
)


async def _test_credentials(hass, username: str, password: str) -> dict[str, str]:
    """Test credentials and return errors dict (empty = success)."""
    session = async_get_clientsession(hass)
    client = SpireClient(session, username, password)
    try:
        await asyncio.wait_for(client.login_only(), timeout=HTTP_TIMEOUT_SECONDS + 10)
    except SpireAuthError:
        return {"base": "invalid_auth"}
    except (SpireApiError, asyncio.TimeoutError):
        return {"base": "cannot_connect"}
    return {}


class SpireGasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Spire Energy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = await _test_credentials(
                self.hass, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            if not errors:
                await self.async_set_unique_id(
                    f"{user_input[CONF_ACCOUNT_ID]}:{user_input[CONF_SA_ID]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Spire Energy ({user_input[CONF_SA_ID]})",
                    data={
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_ACCOUNT_ID: str(user_input[CONF_ACCOUNT_ID]),
                        CONF_SA_ID: str(user_input[CONF_SA_ID]),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> FlowResult:
        """Handle re-authentication when credentials expire."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle re-authentication confirmation."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = await _test_credentials(
                self.hass, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            if not errors:
                self.hass.config_entries.async_update_entry(
                    self._get_reauth_entry(),
                    data={
                        **self._get_reauth_entry().data,
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )
                await self.hass.config_entries.async_reload(
                    self._get_reauth_entry().entry_id
                )
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
