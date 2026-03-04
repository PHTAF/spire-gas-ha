# Spire Energy — Home Assistant Integration

![Spire Energy Logo](custom_components/spire_gas/icon.png)

A custom Home Assistant integration that fetches daily gas usage from
[Spire Energy](https://www.spireenergy.com) and displays it in the
**Energy dashboard** as a gas consumption statistic.

## Features

- Imports full daily usage history available from the Spire Energy API
- Displays in the HA Energy dashboard in **CCF**
- Refreshes automatically every 6 hours to pick up new readings
- No entities or sensors — just a clean statistic in the Energy dashboard

## Data Availability

The amount of historical data available will vary by account. This integration
imports whatever Spire Energy provides — gaps or missing periods in the data
reflect what is available from Spire, not a bug in the integration.

## Requirements

- Home Assistant 2025.1.0 or newer
- A Spire Energy account with online access at
  [myaccount.spireenergy.com](https://myaccount.spireenergy.com)
- Your **Account ID** and **SA ID** (Service Account ID)

### Finding your Account ID and SA ID

Your Account ID is visible on your Spire Energy account overview page after
logging in.

Your SA ID is not directly visible in the Spire Energy web interface. The
easiest way to find it is to log in to
[myaccount.spireenergy.com](https://myaccount.spireenergy.com), open your
browser's developer tools (F12), go to the **Network** tab, navigate to your
usage history page, and look for a request containing `daily-usage-history`.
The SA ID will appear as the `sald` parameter in the request URL.

## Installation via HACS

1. In Home Assistant, go to **HACS → Integrations**
2. Click the three-dot menu in the top right → **Custom repositories**
3. Enter `https://github.com/PHTAF/spire-gas-ha` as the repository URL
4. Select **Integration** as the category
5. Click **Add**
6. Search for **Spire Energy** and click **Download**
7. Restart Home Assistant

## Manual Installation

1. Copy the `custom_components/spire_gas/` folder to your
   `/config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Integrations → Add Integration**
2. Search for **Spire Energy**
3. Enter your Spire Energy credentials:

| Field | Description |
|-------|-------------|
| **Username / Email** | The email address you use to log in to myaccount.spireenergy.com |
| **Password** | Your Spire Energy online account password |
| **Account ID** | Your Spire Energy account number, visible on your account overview page |
| **SA ID** | Your Service Account ID — see above for how to find this |

4. Click **Submit**

## Adding to the Energy Dashboard

1. Go to **Settings → Energy**
2. Under **Gas consumption**, click **Add gas source**
3. Search for **Spire Energy Usage** and select it
4. Click **Save**

Historical data will populate automatically based on what Spire Energy makes
available for your account.

## Removal

1. Go to **Settings → Energy** and remove **Spire Energy Usage** from gas
   consumption sources
2. Go to **Settings → Integrations → Spire Energy → (three dots) → Delete**
3. Go to **Developer Tools → Statistics**, search for `spire_gas` and delete
   the statistic
4. Restart Home Assistant

> **Note:** If you reinstall the integration without deleting the statistic
> first, the integration will skip the historical import since it will see
> existing data. Always delete the statistic before reinstalling if you want
> a clean reimport.

## Troubleshooting

- **No data appearing** — check **Settings → System → Logs** and filter for
  `spire_gas`
- **Authentication error** — your credentials may have changed. The integration
  will prompt you to re-authenticate via the Integrations page
- **Data stops updating** — try reloading the integration from
  **Settings → Integrations → Spire Energy → (three dots) → Reload**

## Contributing

Issues and pull requests welcome at
[github.com/PHTAF/spire-gas-ha](https://github.com/PHTAF/spire-gas-ha).

## License

MIT
