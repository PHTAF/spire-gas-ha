"""Statistics insertion for Spire Energy integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import dt as dt_util

from .api import SpireClient, SpireApiError
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_ACCOUNT_ID, CONF_SA_ID

_LOGGER = logging.getLogger(__name__)


def _safe_float(v: Any) -> Optional[float]:
    try:
        return float(v)
    except Exception:
        return None


def _flatten_usage(payload: dict) -> list[dict]:
    """Flatten premises -> yearlyUsages -> usageDetails."""
    rows = []
    for premise in (payload.get("premises") or []):
        for yearly in (premise.get("yearlyUsages") or []):
            for d in (yearly.get("usageDetails") or []):
                if isinstance(d, dict) and d.get("measuredOn"):
                    rows.append(d)
    return rows


async def async_insert_statistics(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Fetch Spire usage data and write new points to HA long-term statistics."""
    sa_id = entry.data[CONF_SA_ID]
    statistic_id = f"{DOMAIN}:usage_{sa_id}"

    # Find the most recent point already in the DB
    last_stats = await get_instance(hass).async_add_executor_job(
        get_last_statistics, hass, 1, statistic_id, True, {"sum", "state"}
    )

    if last_stats and statistic_id in last_stats:
        last_row = last_stats[statistic_id][0]
        last_ts = last_row.get("start")
        last_sum = last_row.get("sum") or 0.0
        last_date = (
            dt_util.utc_from_timestamp(last_ts).strftime("%Y-%m-%d")
            if isinstance(last_ts, (int, float))
            else None
        )
        _LOGGER.debug("Spire Gas: last recorded point is %s, sum=%.3f", last_date, last_sum)
    else:
        last_date = None
        last_sum = 0.0
        _LOGGER.info("Spire Gas: no existing statistics, doing full import")

    # Fetch from API
    _LOGGER.debug("Spire Gas: fetching usage history for %s", sa_id)
    client: SpireClient = entry.runtime_data
    try:
        payload = await client.get_daily_usage_history(
            entry.data[CONF_ACCOUNT_ID], sa_id
        )
    except SpireApiError as err:
        _LOGGER.error("Spire Gas: API error fetching usage: %s", err)
        return

    rows = _flatten_usage(payload)
    if not rows:
        _LOGGER.warning("Spire Gas: no usage data returned from API")
        return

    by_day: dict[str, float] = {}
    for r in rows:
        day = r.get("measuredOn", "")[:10]
        units = _safe_float(r.get("units"))
        if day and units is not None:
            by_day[day] = units

    if not by_day:
        return

    sorted_days = sorted(d for d in by_day if last_date is None or d > last_date)

    if not sorted_days:
        _LOGGER.debug("Spire Gas: no new data points for %s", statistic_id)
        return

    _LOGGER.info("Spire Gas: inserting %d new points for %s", len(sorted_days), statistic_id)

    tz = dt_util.get_time_zone(hass.config.time_zone)
    running_sum = last_sum
    statistics: list[StatisticData] = []

    for date_str in sorted_days:
        daily_ccf = by_day[date_str]
        running_sum = round(running_sum + daily_ccf, 3)
        year, month, day = map(int, date_str.split("-"))
        start = datetime(year, month, day, 0, 0, 0, tzinfo=tz)
        statistics.append(StatisticData(start=start, state=daily_ccf, sum=running_sum))

    metadata = StatisticMetaData(
        has_mean=False,
        has_sum=True,
        name=f"Spire Energy Usage ({sa_id})",
        source=DOMAIN,
        statistic_id=statistic_id,
        unit_of_measurement="CCF",
    )

    async_add_external_statistics(hass, metadata, statistics)
    _LOGGER.info(
        "Spire Gas: queued %d new points, latest sum=%.3f CCF",
        len(statistics),
        running_sum,
    )
