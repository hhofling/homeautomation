#!/usr/bin/env python3
"""Dump everything on a Fibaro Home Center (HC2/HC3/HC3 Lite) before migrating.

Writes, into ./fibaro-export/ (git-ignored):
  devices.csv     one row per device, with room, type and Z-Wave parent
  rooms.json, devices.json, scenes.json   raw API data
  scenes/<id>-<name>.txt   each scene's Lua or block content, to rebuild in HA

Only reads from the Home Center; it changes nothing.

Usage:
  python3 scripts/fibaro_inventory.py 192.168.1.50 admin
  (you are asked for the password)
"""
import base64
import csv
import getpass
import json
import pathlib
import re
import sys
import urllib.request

OUT = pathlib.Path("fibaro-export")


def get(host, auth, path):
    req = urllib.request.Request(f"http://{host}/api/{path}")
    req.add_header("Authorization", f"Basic {auth}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def safe(name):
    return re.sub(r"[^\w\-]+", "_", str(name)).strip("_")[:60] or "scene"


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    host, user = sys.argv[1], sys.argv[2]
    password = getpass.getpass(f"Password for {user}@{host}: ")
    auth = base64.b64encode(f"{user}:{password}".encode()).decode()

    rooms = get(host, auth, "rooms")
    devices = get(host, auth, "devices")
    scenes = get(host, auth, "scenes")

    OUT.mkdir(exist_ok=True)
    (OUT / "scenes").mkdir(exist_ok=True)
    for name, data in (("rooms", rooms), ("devices", devices), ("scenes", scenes)):
        (OUT / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

    room_names = {r["id"]: r.get("name", "") for r in rooms}
    with open(OUT / "devices.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "room", "type", "baseType", "parentId",
                    "zwave_node", "battery", "migrated_to_ha"])
        for d in sorted(devices, key=lambda d: (d.get("roomID", 0), d["id"])):
            props = d.get("properties", {}) or {}
            interfaces = d.get("interfaces", []) or []
            w.writerow([
                d["id"], d.get("name", ""), room_names.get(d.get("roomID"), ""),
                d.get("type", ""), d.get("baseType", ""), d.get("parentId", ""),
                "yes" if "zwave" in interfaces or str(d.get("type", "")).startswith("com.fibaro") else "",
                "yes" if "battery" in interfaces else "", "",
            ])

    for s in scenes:
        body = s.get("content") or s.get("lua") or s.get("actions") or ""
        if not isinstance(body, str):
            body = json.dumps(body, indent=2, ensure_ascii=False)
        header = (f"-- Scene {s['id']}: {s.get('name', '')}\n"
                  f"-- Room: {room_names.get(s.get('roomId') or s.get('roomID'), '')}\n"
                  f"-- Type: {s.get('type', '')}\n\n")
        (OUT / "scenes" / f"{s['id']}-{safe(s.get('name'))}.txt").write_text(header + body)

    print(f"{len(devices)} devices, {len(rooms)} rooms, {len(scenes)} scenes written to {OUT}/")
    print("Open devices.csv in a spreadsheet and tick off migrated_to_ha as you go.")


if __name__ == "__main__":
    main()
