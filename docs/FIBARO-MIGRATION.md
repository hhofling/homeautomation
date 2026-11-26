# Retiring the Fibaro Home Center: moving Z-Wave to Home Assistant

Goal: every Z-Wave device that is paired to the Fibaro Home Center (HC)
today ends up paired directly to a USB Z-Wave stick on the Home Assistant
box, running Z-Wave JS. Fibaro scenes are rebuilt as Home Assistant
automations. Then the HC is switched off.

Z-Wave devices can only belong to one controller, and Fibaro does not let
you move its network to another controller. So each device is **excluded**
from the HC and **included** again on the stick. Plan about 5 to 10 minutes
per device, plus extra for battery devices and roller shutters.

## What you need

- A USB Z-Wave stick for the **EU frequency (868.4 MHz)**. Good choices:
  Home Assistant Connect ZWA-2, Zooz ZST39 800 LR, Aeotec Z-Stick 7. US/AU
  sticks will not talk to your devices.
- A 0.5 to 1 m USB extension cable. Plugging the stick straight into the
  box (especially next to USB 3 ports or an SSD) causes interference.
- Physical access to every device: you need to press its button or flip
  its switch, often inside a wall box or behind a cover.
- The **S2 PIN / QR code** for each device (the first 5 digits of the DSK
  on a sticker on the device or its box). Photograph them before mounting
  anything back.

## Step 1: Inventory the Fibaro (while it still runs)

From any computer on the same network:

```sh
python3 scripts/fibaro_inventory.py <HC-IP-address> <admin-user>
```

This only reads from the HC. It writes `fibaro-export/` (git-ignored) with:

- `devices.csv`: every device with its room, type and battery flag, plus an
  empty `migrated_to_ha` column to tick off as you go.
- `scenes/`: one text file per scene with its Lua or block content.
- Raw `rooms.json`, `devices.json`, `scenes.json` as a backup.

Also take an HC backup in the Fibaro web UI (Settings > Backup) and write
down any **associations** (devices controlling each other directly, e.g. a
wall switch's second button driving another dimmer) and any special
**parameters** you changed (e.g. dimmer min level, roller shutter type).
These are lost on exclusion and need setting again in Z-Wave JS.

## Step 2: Set up Z-Wave JS

1. Plug the stick in on the extension cable and restart Home Assistant.
2. Settings > Devices & services: Home Assistant offers a **Z-Wave**
   integration for the stick. Accept, and let it install the Z-Wave JS
   add-on. Let it generate new security keys.
3. **Back up the security keys** shown in the add-on configuration
   (S0, S2 Unauthenticated, S2 Authenticated, S2 Access Control) to your
   password manager. Without them a restored or replaced stick cannot talk
   to your secure devices.
4. Optional, for a gradual move: also add the **Fibaro** integration so
   devices still on the HC can be controlled from HA meanwhile.

## Step 3: Move devices one at a time

Start with mains-powered devices closest to the HA box (they build the
mesh that carries signals to the further ones), then work outwards, and do
battery devices last.

For each device:

1. **Exclude** it from the HC: Fibaro UI > device > Advanced/Settings >
   Remove (or Settings > Z-Wave > Remove device), then trigger the device:
   usually triple-click its button (Fibaro modules: triple-click B / S1).
   Z-Wave JS can also exclude any device: Settings > Devices & services >
   Z-Wave > Configure > Remove device. Exclusion works from any controller.
2. **Include** it on HA: Z-Wave > **Add device**. Scan the QR code with the
   HA app, or choose S2 and type the 5-digit PIN when asked, then trigger
   the device the same way. Accept S2 when offered.
3. **Name it and give it an area** straight away, matching the Fibaro name
   and room from `devices.csv`. This keeps entity ids readable
   (`light.kok_tak`, not `light.node_14`).
4. **Re-apply** any changed parameters and associations from Step 1
   (device page > Configure).
5. **Check** it works from HA, then mark it in `devices.csv`.

Device-specific notes:

- **Roller shutters (FGR-222/223, Walli Roller Shutter)**: run the
  calibration again after inclusion (parameter or "Calibrate" button on the
  device page). Set the shutter type parameter again if you had changed it.
- **Dimmers (FGD-212, Walli Dimmer)**: may run auto-calibration on first
  power-up; set the minimum/maximum level parameters again if bulbs flicker.
- **Battery devices (motion sensors, door sensors, smoke sensors,
  thermostats/radiator heads)**: wake them up during inclusion (usually a
  button press or triple-click). Their configuration is applied only at the
  next wake-up, so press the button again after changing parameters.
- **Fibaro Heat Controller / radiator thermostats**: include within 1 to 2
  metres of the stick or a mains-powered node, then mount.
- **Devices that won't exclude** (dead or unreachable): do a factory reset
  on the device (see its manual), then include it fresh. Remove the ghost
  node from the HC afterwards.

After every few devices, run **Rebuild network routes** in Z-Wave >
Configure, especially after the last one.

## Step 4: Rebuild Fibaro scenes as automations

Open each file in `fibaro-export/scenes/` and recreate it in Home
Assistant (Settings > Automations & scenes):

| In Fibaro | In Home Assistant |
|---|---|
| Block scene: "when X then Y" | **Automation** with a trigger, conditions and actions |
| Scene that just sets device states | **Scene** (snapshot of states) |
| Scene triggered by a button press / scene activation | Automation with a **Z-Wave JS: value notification / central scene** trigger (pick the device, then the button and press type) |
| Lua scene with timers / logic | Automation with **time / sun** triggers and **choose** / **if** actions, or a **script** |
| Global variables | **Helpers** (`input_boolean`, `input_number`, `input_select`) |
| Away/Home profile | `input_select.house_mode` in `homeassistant/packages/house_modes.yaml` |
| Climate panel schedules | A schedule helper plus automations, or the Adax/Ebeco app schedules |

Automations you build in the UI are saved to
`homeassistant/automations.yaml`, so copy that file back into this repo to
keep them under version control.

## Step 5: Retire the HC

When every row in `devices.csv` is ticked and every scene is rebuilt:

1. Leave the HC running for a week with nothing on it, in case something
   was missed.
2. Delete the Fibaro integration from Home Assistant if you added it.
3. Factory-reset the HC (so it does not hold old credentials), then switch
   it off.
