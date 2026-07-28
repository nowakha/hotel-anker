---
name: ubiquiti-unifi
description: >-
  Operates Hotel Anker UniFi (UDM Pro Max + U7 Pro Wall) safely via console,
  SSH read-only inventory, and Hotspot Landing Page workflow. Use when the user
  mentions UniFi, Ubiquiti, Dream Machine, UDM, U7, guest WiFi, HotelAnkerGuest,
  captive portal, or Hotel Anker LAN/VLAN changes.
---

# Ubiquiti UniFi — Hotel Anker

## Scope

Hotel Anker site only: **UDM Pro Max** + **U7 Pro Wall**. Secrets:
[`WerbeLEDbox-CountDown/secrets/unifi.hotelanker.yml`](../../../WerbeLEDbox-CountDown/secrets/unifi.hotelanker.yml).
Network map: [`WerbeLEDbox-CountDown/docs/NETWORK_UNIFI.md`](../../../WerbeLEDbox-CountDown/docs/NETWORK_UNIFI.md).

## Hard rules (no exceptions)

1. **Read-only first** — inventory before any change.
2. **Never** `factory-reset.sh`, never reboot the UDM unless the user explicitly asks.
3. **Never** write MongoDB `ace` for portal/WLAN branding — use UniFi UI / official API only.
4. **Never** paste `x_api_token`, device SSH passwords, or PSKs into markdown docs — secrets YAML only.
5. **One change at a time**, then verify AP online + SSIDs + AnkerPIs on `192.168.1.x` (Administration).
6. **No live apply** of guest portal or DHCP/VLAN edits until the user explicitly approves that change.
7. Prefer **Insights → Hotspot → Landing Page** for branding. Exception: if the portal SPA is missing (`index.html` 404 / empty body), restore the stock package with `scripts/repair_unifi_hotspot_portal.py` (no mongo writes).

## Access

| Path | Value |
|------|--------|
| Console | `https://192.168.1.254` |
| SSH | `root@192.168.1.254` (password in secrets) |
| Gateway LAN | `192.168.1.254/24` (Default) |

UI admin may differ from SSH root — if API login returns 403, do not brute-force; ask for UI credentials or use documented UI steps.

## Site map (SSID ↔ VLAN)

| SSID | Network | Subnet |
|------|---------|--------|
| `Administration` | Default | `192.168.1.0/24` |
| `HotelAnker` | CountDown Bar (VLAN 2) | `192.168.2.0/24` |
| `HotelAnkerGuest` | Guest Network (VLAN 3) | `192.168.3.0/24` |

- Tri-band single SSIDs (2.4/5/6) — **do not** recreate legacy `HotelAnker_5G` as primary.
- AnkerPI01/02 live on **Administration** (`.1.x`), PSK `HeimatSchutz` — not Bar VLAN `.2.x`.
- Migrate script: `scripts/migrate_pis_to_administration_wifi.py` (SSH jump via UDM).

## Read-only inventory (SSH)

```bash
ssh root@192.168.1.254
ubnt-device-info summary
ip -br addr
ip -4 route show table all | head -40
cat /data/udapi-config/dnsmasq.lease
```

Mongo **read** (never update):

```bash
mongo --quiet --port 27117 ace --eval '
db.wlanconf.find({},{name:1,security:1,is_guest:1,networkconf_id:1,enabled:1}).forEach(printjson);
db.networkconf.find({},{name:1,purpose:1,vlan:1,ip_subnet:1,dhcpd_start:1,dhcpd_stop:1}).forEach(printjson);
db.device.find({},{name:1,model:1,ip:1,mac:1,type:1,version:1,adopted:1}).forEach(printjson);
db.setting.find({key:"guest_access"}).forEach(printjson);
'
```

From Windows, use Paramiko (password from secrets) — OpenSSH password prompts are awkward in agents.

## Guest portal workflow

1. Build/review local mockup: `WerbeLEDbox-CountDown/guest-wifi-portal/`
2. Assets: `guest-wifi-portal/exports/` (logo PNG, optional BG JPEG)
3. After user visual OK → UniFi Network → **Insights → Hotspot → Landing Page**
4. Map fields from [`NETWORK_UNIFI.md`](../../../WerbeLEDbox-CountDown/docs/NETWORK_UNIFI.md) § Landing Page
5. Verify on a phone connected to `HotelAnkerGuest` (open SSID + captive portal)
6. Keep `auth=none` + Terms of Service unless user requests password/vouchers

## After any approved WiFi/VLAN change

- [ ] U7 still adopted / reachable (`192.168.1.220`)
- [ ] `Administration` and `HotelAnker` associate
- [ ] Guest portal loads on `HotelAnkerGuest`
- [ ] AnkerPI01/02 still on `192.168.2.x` (SSH/Tailscale)

## More detail

See [reference.md](reference.md) for CLI notes, DHCP pitfalls, and anti-patterns.
