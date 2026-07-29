# UniFi reference — Hotel Anker

## Hardware

| Device | Model | Role | LAN IP |
|--------|-------|------|--------|
| Dream Machine Pro Max | UDMPROMAX | Gateway + controller | `192.168.1.254` |
| U7 Pro Wall | U7PIW | AP (2.4/5/6 GHz) | `192.168.1.220` |

Firmware observed 2026-07-28: UDM **5.1.27**, AP **8.6.11**.

## WAN note

WAN on `eth7` may show ISP CGNAT (`10.x` via `10.0.0.1`). Internet works via policy routing table `201.eth7`. Do not “fix” WAN to a public IP unless ISP changed.

## DHCP pitfalls

- Default pool must **exclude** the gateway (`192.168.1.254`). A pool ending at `.254` can hand out the gateway address.
- Remove bogus static leases (`00:00:00:00:00:00`).
- Prefer static DHCP for AnkerPI01/02 on CountDown Bar (`192.168.2.0/24`).

## Guest / Hotspot

- SSID `HotelAnkerGuest` is **open**; auth is captive portal (`auth=none`).
- Guest network purpose=`guest` + restricted RFC1918 subnets — clients should not reach staff/Bar LAN (`192.168.1/24`, `192.168.2/24` in `UBIOS_corporate_network`).
- L2 isolation on the guest WLAN; traffic on `br3` → `UBIOS_GUEST_IN_USER`.
- Session expire default: 480 minutes (8 h).
- Brand via UI Landing Page; set `portal_customized` through UI, not mongo.
- Live portal URL: `http://192.168.1.254:8880/guest/s/default/` — config JSON: `…/hotspotconfig`.
- Connect (auth=none): `POST /guest/s/default/login` with empty JSON body + `ec` cookie → `authorized:true`.

### Broken empty portal (known failure)

If `curl` to `:8880/guest/s/default/` returns **Content-Length 0** and logs show
`FileNotFoundException …/app-unifi-hotspot-portal/index.html`, re-extract the stock SPA:

`ace.jar` → `BOOT-INF/lib/internal-dependencies.jar` → `app-unifi-hotspot-portal.zip`
into `/data/unifi/data/sites/default/app-unifi-hotspot-portal/`.

Script: `WerbeLEDbox-CountDown/scripts/repair_unifi_hotspot_portal.py`.  
This is a **package restore**, not custom template editing.

## SSH vs device SSH

- **Console SSH** (`root@192.168.1.254`): UniFi OS Control Plane → Console → SSH.
- **Device SSH** (AP credentials in `mgmt` setting): separate random user/pass — do not document in git markdown.

## Anti-patterns

- Recreating dual SSIDs `HotelAnker` + `HotelAnker_5G` (legacy Pi docs) — UniFi uses one tri-band SSID.
- `ffmpeg`-style full-file probes on the UDM — N/A; do not load the controller with huge SCP dumps mid-service.
- Editing `/data/unifi` portal templates over SSH on modern UniFi OS Hotspot UI.
- Applying several VLAN/SSID/DHCP changes in one session without verifying PIs.

## Useful paths on UDM

| Path | Use |
|------|-----|
| `/data/udapi-config/dnsmasq.lease` | DHCP leases |
| `/data/udapi-config/udapi-net-cfg.json` | Low-level net config (read) |
| `/data/unifi/data/` | Controller data |
| `/data/unifi/logs/hotspot.log` | Portal log |
| `/data/unifi/data/sites/default/app-unifi-hotspot-portal/` | Captive portal SPA |

## Docs / scripts

| File | Use |
|------|-----|
| `WerbeLEDbox-CountDown/docs/NETWORK_UNIFI.md` | Inventory + guest checklist |
| `WerbeLEDbox-CountDown/scripts/repair_unifi_hotspot_portal.py` | Restore missing portal SPA |
