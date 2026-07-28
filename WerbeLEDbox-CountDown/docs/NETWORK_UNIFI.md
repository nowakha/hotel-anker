# UniFi Network — Hotel Anker

Stand: 2026-07-29 (verifiziert).

## Geräte

| Gerät | IP | Firmware |
|-------|-----|----------|
| UDM Pro Max | `192.168.1.254` | UniFi OS / Network **10.5.67** |
| U7 Pro Wall | `192.168.1.220` | **8.6.11** |

Secrets: `secrets/unifi.hotelanker.yml`  
Skill: `.cursor/skills/ubiquiti-unifi/`

## SSIDs ↔ VLANs

| SSID | Netzwerk | Subnetz | Auth (UniFi) | Geräte |
|------|----------|---------|--------------|--------|
| `Administration` | Default | `192.168.1.0/24` | **WPA2/WPA3 Transition**, PMF optional, PSK `HeimatSchutz` | **AnkerPI01/02**, Staff, UDM |
| `HotelAnker` | CountDown Bar (VLAN 2) | `192.168.2.0/24` | WPA2/WPA3 Transition, PMF optional | Bar / Event |
| `HotelAnkerGuest` | Guest (VLAN 3) | `192.168.3.0/24` | Open + E-Mail-Portal | Gäste |

PSK: [`../secrets/wifi.hotelanker.yml`](../secrets/wifi.hotelanker.yml).  
Skript Umzug Pis → Administration: [`../scripts/migrate_pis_to_administration_wifi.py`](../scripts/migrate_pis_to_administration_wifi.py) (Jump über UDM / Tailscale).

### WPA3 / Pi Zero 2 W (kritisch)

- **AnkerPI01** = Pi Zero 2 W (CYW43436 / BCM43430): **kein zuverlässiges WPA3-only (SAE)**.
- Administration muss **WPA2/WPA3 Transition** bleiben (`wpa3_transition=true`, `pmf_mode=optional`) — verifiziert 2026-07-29.
- Früher WPA3-only + `pmf=required` → PI01 konnte nicht associieren; Scan zeigte `Administration:WPA3`.
- NM-Profil auf Pis: `wifi-sec.key-mgmt=wpa-psk` (nicht `sae`). Pi 4 (PI02) ebenfalls Transition-fähig.
- Vor jedem Migrate: UniFi `wlanconf` + `nmcli device wifi list` SECURITY-Spalte prüfen.

## Gäste-WLAN — Sollzustand

- SSID offen, `is_guest=true`, **L2 Isolation** an
- **E-Mail-Portal** (lokal auf UDM): `auth=custom`, `custom_ip=192.168.1.254`
- Entry: Captive Redirector → `http://192.168.1.254/guest/…` (nginx :80 → Portal **:9090**); Fallback Bridge von `:8880`
- Pflicht: E-Mail + Einwilligung (DE/EN/FR/IT/**Rumantsch**); bekannte MAC → kein erneutes Formular
- Speicher: SQLite + CSV unter `/data/hotel-anker/guest-emails/`
- Session / Token: **120 Min (2 h)** — danach erneut verbinden; bei bekannter MAC ohne neue E-Mail
- Firewall: Portal-Ports in `UBIOS_guest_portal_ports` inkl. **80** und **9090**; RFC1918 + Corporate für Unautorisierte geblockt

### Guest-E-Mail-Portal (Dienst)

Pfad im Repo: `guest-email-portal/`  
Install/Repair: [`../scripts/install_guest_email_portal.py`](../scripts/install_guest_email_portal.py)  
Export (Cursor: „E-Mails exportieren“): [`../scripts/export_guest_emails.py`](../scripts/export_guest_emails.py)

```bash
systemctl status hotel-anker-guest-portal.service
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9090/health
curl -sS -o /dev/null -w "%{http_code}\n" "http://127.0.0.1/guest/s/default/?id=aa:bb:cc:dd:ee:ff"
```

Nach UDM-/Network-Update oft nötig: Install-Skript erneut; `ipset` Ports 80/9090; nginx-:80-Snippet für `/guest/` → `:9090`.

**iPhone:** „Private WLAN-Adresse“ für `HotelAnkerGuest` aus — sonst neue Random-MAC und erneut E-Mail-Formular.

### Captive-Portal-App reparieren (Legacy SPA :8880)

Symptom: Portal liefert HTTP 200 mit **leerem Body**; Log `FileNotFoundException …/app-unifi-hotspot-portal/index.html`.

Ursache: unter `/data/unifi/data/sites/default/app-unifi-hotspot-portal/` fehlen Root-Dateien (nur `static/` übrig).

Fix (SSH, kein Mongo-Schreiben): Paket aus `ace.jar` → `BOOT-INF/lib/internal-dependencies.jar` → `app-unifi-hotspot-portal.zip` nach dem Portal-Pfad extrahieren.

Skript: [`../scripts/repair_unifi_hotspot_portal.py`](../scripts/repair_unifi_hotspot_portal.py)

Hinweis: Login-Pfad ist das E-Mail-Portal auf **:9090**; `:8880/index.html` bridged dorthin.

### Logo + Hintergrund (live)

- Logo: Anker — Portal-Asset `guest-email-portal/static/logo-anchor-gold.svg` (und Legacy SPA Media)
- Hintergrund: Hotel-Outline Cover — `hotel-anker-outline-bg.jpg`
- Quelle Outline: `WerbeLEDbox-CountDown/assets/hotel-anker-blueprint-simplified.png`

### Handy-Test

1. Mit `HotelAnkerGuest` verbinden → Captive-Portal öffnet E-Mail-Landing (5 Sprachen inkl. Rumantsch)
2. Neue MAC: E-Mail + Checkbox → Success („Fertig tippen“), kein Google-Redirect
3. Nach ≤2 h oder Token-Reset: Portal erneut; **bekannte MAC** → sofort Success ohne Formular
4. Gleiche E-Mail erneut → **kein** zweiter Tabellen-Eintrag (Update MAC/`last_seen`)
5. Kein Zugriff auf `192.168.1.x` / `192.168.2.x` (Staff / Bar)

## Offene Härten (nur mit expliziter Freigabe)

- Guest `mdns_enabled: true` → besser aus
- Default-DHCP-Pool endet ggf. inkl. `.254` → Gateway ausschließen
- Logo-Upload (API oft `NoPermission`) → manuell in Insights → Hotspot → Landing Page
- Statische DHCP-Reservierungen für AnkerPIs
- nginx-:80-Patch und systemd-Unit nach großen UniFi-OS-Updates prüfen
