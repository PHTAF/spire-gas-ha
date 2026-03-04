"""Spire Energy integration.

Fetches daily gas usage from the Spire Energy API and writes it
to HA long-term statistics for display in the Energy dashboard.

Statistic ID : spire_gas:usage_{sa_id}
Unit         : CCF

Refreshes every 6 hours. On each run, only new data points are appended.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

from .api import SpireClient, SpireApiError, SpireAuthError
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, UPDATE_INTERVAL_HOURS
from .statistics import async_insert_statistics

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(hours=UPDATE_INTERVAL_HOURS)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Spire Energy from a config entry."""

    # Create API client and verify credentials work — test-before-setup
    session = async_get_clientsession(hass)
    client = SpireClient(session, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])

    try:
        await client.login_only()
    except SpireAuthError as err:
        raise ConfigEntryAuthFailed("Invalid credentials") from err
    except SpireApiError as err:
        raise ConfigEntryNotReady("Could not connect to Spire API") from err

    # Store client in runtime_data — the modern HA pattern
    entry.runtime_data = client

    async def _refresh(_now=None) -> None:
        await async_insert_statistics(hass, entry)

    # Run immediately on setup
    hass.async_create_task(_refresh())

    # Schedule recurring refresh every 6 hours
    cancel = async_track_time_interval(hass, _refresh, UPDATE_INTERVAL)

    # Store cancel callback for cleanup on unload
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = cancel

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    cancel = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if cancel:
        cancel()
    return True
