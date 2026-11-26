# Home automation

One Home Assistant hub for every system in the house: Fibaro Home Center,
Philips Hue, Samsung SmartThings, Plejd, Adax, Ebeco Connect, TP-Link Tapo,
Google Home/Nest and anything Matter or Zigbee.

- `homeassistant/`: Home Assistant config (`/config` on the HA box)
  - `packages/house_modes.yaml`: cross-brand house modes (Hemma/Borta/Natt/Semester) that lower heating and turn off lights across all brands
- `esphome/plejd-bluetooth-proxy.yaml`: ESP32 Bluetooth proxy so HA reaches Plejd from anywhere
- `docs/INTEGRATIONS.md`: per-brand integration route, credentials needed and limits
- `.github/workflows/check-config.yml`: validates the HA config on every push

## What you need to do yourself

Credentials never go in this repo. You need:

1. **Hardware**: a Home Assistant box (Home Assistant Green, Raspberry Pi 5 or mini PC). Optional: one ESP32 board (~100 kr) as a Plejd Bluetooth proxy.
2. **Fibaro**: HC IP address and a dedicated Fibaro user with password.
3. **Hue**: be by the bridge to press its button.
4. **SmartThings**: your Samsung account login.
5. **Plejd**: Plejd app email and password.
6. **Adax**: Account ID and API password from the Adax app (Account > Third party integrations > Remote API).
7. **Ebeco Connect**: Ebeco app email and password.
8. **Tapo**: TP-Link account email and password; fixed IPs in your router; for cameras, a camera account set in the Tapo app.
9. **Google**: for Nest thermostats/cameras, a Device Access registration (US$5); for "Hey Google" voice control, a Home Assistant Cloud subscription.

Then follow the setup order in [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md).
