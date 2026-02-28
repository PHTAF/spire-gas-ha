# Spire Gas — Home Assistant Integration

A custom Home Assistant integration that fetches daily gas usage from
[Spire Energy](https://www.spireenergy.com) and displays it in the
**Energy dashboard** as a gas consumption statistic.

## Features

- Imports full daily usage history from the Spire API
- Displays in the HA Energy dashboard in **CCF**
- Refreshes automatically every 6 hours to pick up new readings
- No entities or sensors — just a clean statistic in the Energy dashboard

## Requirements

- Home Assistant 2024.1 or newer
- A Spire Energy account with online access
- Your **Account ID** and **SA ID** (Service Account ID) from your Spire account

### Finding your Account ID and SA ID

Log in to [myaccount.spireenergy.com](https://myaccount.spireenergy.com). Your
Account ID and SA ID are visible in the URL when viewing your usage history, or
on your account overview page.

## Installation via HACS

1. In Home Assistant, go to **HACS → Integrations**
2. Click the three-dot menu in the top right → **Custom repositories**
3. Enter `https://github.com/PHTAF/spire-gas-hacs` as the repository URL
4. Select **Integration** as the category
5. Click **Add**
6. Search for **Spire Gas** and click **Download**
7. Restart Home Assistant

## Manual Installation

1. Copy the `custom_components/spire_gas/` folder to your
   `/config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Integrations → Add Integration**
2. Search for **Spire Gas**
3. Enter your Spire credentials:
   - **Username** — your Spire online account email
   - **Password** — your Spire online account password
   - **Account ID** — your Spire account number
   - **SA ID** — your service account ID
4. Click **Submit**

## Adding to the Energy Dashboard

1. Go to **Settings → Energy**
2. Under **Gas consumption**, click **Add gas source**
3. Search for **Spire Gas Usage** and select it
4. Click **Save**

Historical data going back up to 2 years will populate automatically.

## Notes

- Spire's API only returns January and December for the oldest available year.
  This causes a visible gap in historical data for that year — this is a
  limitation of the Spire API, not a bug in this integration.
- Statistics are written to the HA recorder database. If you uninstall and
  reinstall, delete the `spire_gas:usage_*` statistic from
  **Developer Tools → Statistics** first so the full history reimports cleanly.

## Contributing

Issues and pull requests welcome at
[github.com/PHTAF/spire-gas-hacs](https://github.com/PHTAF/spire-gas-hacs).

## License

MIT
