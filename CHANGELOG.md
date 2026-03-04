# Changelog

All notable changes to this project will be documented here.

## [1.3.0] - 2026-03-04

### Added
- Reauthentication flow — HA will prompt to re-enter credentials if they expire
- `data_description` fields in config flow for clearer setup guidance
- `statistics.py` as a separate module for statistics logic
- Removal instructions to documentation
- Configuration parameters table in documentation

### Changed
- Renamed integration display name from "Spire Gas" to "Spire Energy"
- Updated statistic name to "Spire Energy Usage"
- Updated minimum Home Assistant version to 2025.1.0
- API client now stored in `entry.runtime_data` (modern HA pattern)
- Setup now raises `ConfigEntryAuthFailed` or `ConfigEntryNotReady` on failure
- Login verified on setup before completing integration initialization
- Removed inaccurate note about data being one month behind

## [1.2.2] - 2026-03-01

### Fixed
- Moved brand folder to correct location inside `custom_components/spire_gas/`

## [1.2.1] - 2026-03-01

### Added
- Brand directory with icon for display in the HA integrations page

## [1.2.0] - 2026-02-28

### Added
- Automatic refresh every 6 hours to pick up new Spire readings
- Only appends new data points on each refresh — does not rewrite history

### Changed
- Live API fetch replaces static data

## [1.1.0] - 2026-02-28

### Added
- Live data fetch from Spire Energy API on setup

### Removed
- Static hardcoded data

## [1.0.0] - 2026-02-28

Initial public release.

- Fetches daily gas usage history from Spire Energy API
- Displays in Home Assistant Energy dashboard in CCF
- UI-based configuration via config flow
- HACS compatible
