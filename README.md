# EAM Meter Readout Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

Submit meter readings to the EAM customer portal (eam.mein-portal.de) from Home Assistant.

## Features

- 📤 Service to submit readings from any energy entity
- 📊 Sensor showing last submitted readout and date from portal
- ✅ Validates new reading is greater than last reading
- 🔒 Prevents duplicate submissions in the same month
- 🔐 Secure authentication with EAM portal

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

## Usage

**Service**: `eam_meter.submit_readout`  
**Sensor**: `sensor.eam_meter_last_readout` (updates every 6 hours and after submission)

### Example Automation

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
      - service: eam_meter.submit_readout
```

## Troubleshooting

**Cannot Connect**: Check internet connection and EAM portal availability  
**Invalid Auth**: Verify username and password  
**Already submitted this month**: Only one submission per month is allowed

Enable debug logging:
```yaml
logger:
  logs:
    custom_components.eam_meter: debug
```

---

**Author**: [@Julian0021](https://github.com/Julian0021)
