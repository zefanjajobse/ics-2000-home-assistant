# Home Assistant KlikAanKlikUit ICS-2000 support
This custom component adds the dimmable lights and switches from the ICS-2000 from KlikAanKlikUit to Home Assistant. It uses [this](https://github.com/zefanjajobse/ics_2000_python) python package, to connect with the ICS-2000.

# Installation
1. Add the ics_2000 folder within custom_components to your own home assistant installation, in your own custom_components folder.
2. add the light configuration with the username and password for your ICS-2000

```yaml
light:
  - platform: ics_2000
    username: !secret ics_username
    password: !secret ics_password
```
