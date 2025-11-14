# EAM Meter - Home Assistant Custom Component

Home Assistant integration for posting meter readouts to the EAM portal.

## Installation

### Manual Installation

1. Copy the `custom_components/eam_meter` directory to your Home Assistant `custom_components` folder:
   ```
   /config/custom_components/eam_meter/
   ```

2. Restart Home Assistant

3. Add the integration via UI:
   - Go to **Settings** → **Devices & Services**
   - Click **+ Add Integration**
   - Search for "EAM Meter"
   - Enter your EAM portal username and password

## Usage

The integration creates two entities:

### Number Entity: `number.eam_meter_meter_readout`
- Input field for entering your meter reading in kWh
- Range: 0 to 999,999 kWh

### Button Entity: `button.eam_meter_submit_readout`
- Press to submit the readout to the EAM portal
- Uses the value from the number entity

## Example Automation

```yaml
automation:
  - alias: "Submit Meter Readout Monthly"
    trigger:
      - platform: time
        at: "08:00:00"
      - platform: template
        value_template: "{{ now().day == 1 }}"
    action:
      - service: number.set_value
        target:
          entity_id: number.eam_meter_meter_readout
        data:
          value: 12345  # Replace with your actual reading
      - service: button.press
        target:
          entity_id: button.eam_meter_submit_readout
```

## Lovelace Card Example

```yaml
type: entities
title: EAM Meter Readout
entities:
  - entity: number.eam_meter_meter_readout
  - entity: button.eam_meter_submit_readout
```

## Troubleshooting

Check Home Assistant logs for errors:
```
Settings → System → Logs
```

Look for entries containing `eam_meter`.
