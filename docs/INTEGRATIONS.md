# Integration plan: every brand into Home Assistant

Home Assistant (HA) is the hub. Each brand is connected the best way
available, preferring **local** control (works without internet, faster)
over **cloud** control.

| Brand | How it connects | Local or cloud | What you need | Limits |
|---|---|---|---|---|
| Fibaro Home Center (HC2/HC3/HC3 Lite) | Built-in **Fibaro** integration | Local | HC IP address, a Fibaro user + password (make a dedicated user) | Z-Wave devices stay paired to the Fibaro; HA controls them through it. Scenes on the HC show up as scenes. Long-term, you can move Z-Wave devices to HA with a Z-Wave stick and retire the HC. |
| Philips Hue | Built-in **Philips Hue** integration | Local | Press the button on the Hue Bridge during setup | None worth noting. Hue scenes and motion sensors come through. |
| Samsung SmartThings | Built-in **SmartThings** integration (new OAuth version since HA 2025.3) | Cloud | Samsung account login in the browser | Cloud-dependent. No personal access token needed any more. Zigbee/Z-Wave devices on a SmartThings hub stay there. |
| Plejd | **HACS** custom integration ([thomasloven/hass-plejd](https://github.com/thomasloven/hass-plejd)) | Local (Bluetooth mesh) | Plejd app email + password (used once to fetch the mesh key); Bluetooth in range of one Plejd device | HA must reach the Plejd mesh over Bluetooth. If the HA box is far away, use the ESP32 proxy in `esphome/plejd-bluetooth-proxy.yaml`. The Plejd gateway (GWY-01) is **not** used by HA. |
| Adax heaters | Built-in **Adax** integration | Cloud or local | Cloud: Account ID + API password from the Adax app (Account > Third party integrations > Remote API). Local (newer Wi-Fi heaters only): set up over Bluetooth from HA | Local mode re-provisions the heater onto Wi-Fi directly and it then leaves the Adax app; pick one mode. |
| Ebeco Connect (floor heating) | **HACS** custom integration ([joggs/home_assistant_ebeco](https://github.com/joggs/home_assistant_ebeco)) | Cloud only | Ebeco Connect app email + password | No local API. If Ebeco's cloud is down, HA can't control the thermostats. |
| TP-Link Tapo plugs/bulbs/strips/hubs | Built-in **TP-Link Smart Home** integration | Local | TP-Link/Tapo cloud email + password (used to authenticate locally) | Give devices fixed IPs in the router. Turn on "Third-Party Compatibility" in the Tapo app (Me > Tapo Lab) if setup fails. |
| TP-Link Tapo cameras | **HACS** [JurajNyiri/HomeAssistant-Tapo-Control](https://github.com/JurajNyiri/HomeAssistant-Tapo-Control) | Local | Camera account (set in Tapo app: camera > Advanced > Camera Account) | Some newer models also work in the built-in TP-Link integration. |
| Google Home: Nest speakers/displays, Chromecast | Built-in **Google Cast** | Local | Nothing, auto-discovered | Media control and TTS only. |
| Google Nest thermostat/cameras/doorbell | Built-in **Google Nest** | Cloud | Google Device Access registration (one-off US$5 fee) and a Google Cloud project | Setup is fiddly; follow the HA docs step by step. |
| Google Home voice control of everything | **Home Assistant Cloud** (Nabu Casa) or manual **Google Assistant** integration | Cloud | Nabu Casa subscription (easiest), or a free but complex Google Cloud project | Lets you say "Hey Google, turn off the kitchen" for Plejd, Adax, Ebeco etc. |
| Matter / Thread devices (incl. new Google, Ikea, Eve, etc.) | Built-in **Matter** + Matter Server add-on | Local | Share the device from Google Home/SmartThings to HA ("multi-admin") | Thread devices need a Thread border router (Nest Hub 2nd gen/Nest Wifi Pro works, or an HA Connect ZBT-1/ZBT-2). |
| Other (Zigbee: Ikea, Aqara...) | Built-in **ZHA** or Zigbee2MQTT | Local | A Zigbee coordinator (HA Connect ZBT-1/ZBT-2, SONOFF dongle) | Only if you have Zigbee devices not already on a Hue/SmartThings hub. |

Swedish extras worth adding later: **Nord Pool** (built in, hourly
electricity prices, great for running Adax/Ebeco heating cheaply) and
**Tibber** if that is your electricity supplier.

## Setup order

1. **Install Home Assistant OS** on a Home Assistant Green, a Raspberry Pi 5
   or a small mini PC. Wired Ethernet, close to the middle of the house if
   possible (helps Plejd Bluetooth).
2. **Copy this repo's `homeassistant/` folder** onto the box (Samba or
   Studio Code Server add-on) and copy `secrets.yaml.example` to
   `secrets.yaml` with your real coordinates.
3. **Install HACS** (https://hacs.xyz) and restart.
4. **Add the local integrations first**: Hue, Fibaro, TP-Link, Google Cast,
   Adax. Settings > Devices & services > Add integration.
5. **Plejd**: HACS > search "Plejd" > install > restart > add the
   integration with your Plejd login. If no devices show up, flash an ESP32
   with `esphome/plejd-bluetooth-proxy.yaml` and put it near a Plejd unit.
6. **Ebeco**: HACS > Custom repositories > add
   `https://github.com/joggs/home_assistant_ebeco` (Integration) > install >
   restart > add with your Ebeco Connect login.
7. **SmartThings**: add the integration and log in to Samsung.
8. **Google**: Nest via Device Access if you have Nest thermostats/cameras;
   then Home Assistant Cloud > Google Assistant for voice control.
9. **Areas and groups**: put every device in an area (Kök, Vardagsrum...),
   then fill in `group.all_lights` and `group.all_heaters` in
   `homeassistant/packages/house_modes.yaml`.

## Avoiding double control

When a device is in two systems (e.g. Hue lights also in SmartThings or
Google Home), add it to HA from **one** source only, the local one. In this
house: Hue directly, not via SmartThings; Fibaro devices via Fibaro; Tapo
via the TP-Link integration, not via Google. Disable the duplicate entities
in HA if they appear.
