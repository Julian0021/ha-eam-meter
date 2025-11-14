# EAM Meter Readout Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

A Home Assistant integration that allows you to automatically submit meter readings to the EAM customer portal (eam.mein-portal.de).

## Features

- 🔐 Secure authentication with EAM portal credentials
- 📊 Automatic meter reading submission from any Home Assistant sensor
- 🔘 Easy-to-use button entity for manual submission
- ⚙️ Simple configuration through the UI
- 🔄 Works with energy sensors, input numbers, and custom meter entities

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Download the `eam_meter` folder from this repository
2. Copy it to your Home Assistant `custom_components` directory:
   ```
   <config_directory>/custom_components/eam_meter/
   ```
3. Restart Home Assistant

## Configuration

### Step 1: Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **EAM Meter Readout**
4. Click on it to start the configuration flow

### Step 2: Enter Your Credentials

You'll need to provide:

- **Username**: Your EAM portal username
- **Password**: Your EAM portal password
- **Meter Reading Entity**: Select the entity that contains your current meter reading (e.g., a sensor, input_number, or number entity)

The integration will validate your credentials and create the necessary entities.

## Usage

### Submit Meter Reading

Once configured, the integration creates a button entity:

**Entity**: `button.eam_meter_submit_readout`

To submit your meter reading:

1. **Via UI**: Go to the device page and press the "Submit Readout" button
2. **Via Automation**: Use the `button.press` service in your automations
3. **Via Script**: Call the button press action in scripts

### Example Automation

Submit meter readings automatically on the first day of each month:

```yaml
automation:
  - alias: "Submit EAM Meter Reading Monthly"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: template
        value_template: "{{ now().day == 1 }}"
    action:
      - service: button.press
        target:
          entity_id: button.eam_meter_submit_readout
```

### Example with Notification

Get notified when the reading is submitted:

```yaml
automation:
  - alias: "Submit Meter Reading with Notification"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: template
        value_template: "{{ now().day == 1 }}"
    action:
      - service: button.press
        target:
          entity_id: button.eam_meter_submit_readout
      - service: notify.mobile_app
        data:
          title: "Meter Reading Submitted"
          message: "EAM meter reading submitted: {{ states('sensor.your_meter_entity') }} kWh"
```

## Supported Entity Types

The integration works with any entity that has a numeric state, including:

- ✅ `sensor.*` - Energy sensors (e.g., from energy meters)
- ✅ `input_number.*` - Manual input helpers
- ✅ `number.*` - Number entities

The value will be converted to an integer (kWh) before submission.

## How It Works

When you press the submit button, the integration:

1. Reads the current value from your configured entity
2. Authenticates with the EAM portal using your credentials
3. Retrieves the meter metadata from your account
4. Submits the reading with today's date
5. Confirms successful submission

All communication happens securely over HTTPS with the EAM portal.

## Requirements

- Home Assistant 2023.1.0 or newer
- Valid EAM customer portal account
- Python package: `requests`

## Troubleshooting

### "Cannot Connect" Error

- Verify your internet connection
- Check if the EAM portal is accessible: https://eam.mein-portal.de
- Ensure your Home Assistant instance can reach external websites

### "Invalid Auth" Error

- Double-check your username and password
- Try logging in manually to the EAM portal to verify credentials
- Make sure your account is active

### "Invalid Readout Value" Error

- Ensure your selected entity has a valid numeric state
- Check that the entity is available and not in an unknown/unavailable state
- The value must be a positive number

### Enable Debug Logging

Add this to your `configuration.yaml` to see detailed logs:

```yaml
logger:
  default: info
  logs:
    custom_components.eam_meter: debug
```

## Development

This integration is built with:

- Python 3.11+
- Home Assistant Core
- Requests library for HTTP communication

### File Structure

```
eam_meter/
├── __init__.py          # Integration setup
├── button.py            # Button entity implementation
├── config_flow.py       # Configuration UI flow
├── const.py             # Constants and configuration
├── eam_api.py           # EAM portal API client
├── manifest.json        # Integration metadata
├── strings.json         # UI strings
└── translations/
    └── en.json          # English translations
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Enable debug logging and check your Home Assistant logs
3. Open an issue on GitHub with relevant log excerpts

## License

This project is provided as-is for personal use.

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by EAM. Use at your own risk.

---

**Author**: [@Julian0021](https://github.com/Julian0021)  
**Version**: 1.0.0  
**Last Updated**: November 2025
