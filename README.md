# EAM Meter Readout Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

Submit meter readings to the EAM customer portal (eam.mein-portal.de) from Home Assistant.

## Features

- 📤 Button to submit readings from any numeric entity
- 📊 Sensor showing last submitted readout from portal
- 🔐 Secure authentication with EAM portal
- 🔄 Auto-refresh sensor after submission

## Installation

### HACS

1. Add this repository as a custom repository in HACS
2. Install "EAM Meter Readout"
3. Restart Home Assistant

### Manual

1. Copy `custom_components/eam_meter` to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **EAM Meter Readout**
3. Enter your EAM portal username and password
4. Select the entity containing your meter reading

## Entities

- `button.eam_meter_submit_readout` - Submit current reading to portal
- `sensor.eam_meter_last_readout` - Last submitted reading (updates every 6 hours and after button press)

## Example Automation

Submit monthly on the 1st at 9 AM:

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

## Troubleshooting

**Cannot Connect**: Check internet connection and EAM portal availability  
**Invalid Auth**: Verify username and password  
**Invalid Readout Value**: Ensure selected entity has a valid numeric state

Enable debug logging:
```yaml
logger:
  logs:
    custom_components.eam_meter: debug
```

---

**Author**: [@Julian0021](https://github.com/Julian0021)
