#!/usr/bin/env bash
# Run on AnkerPI02 after hex files were copied to /tmp/anker_teensy_flash
set -euo pipefail

DIR="${FLASH_DIR:-/tmp/anker_teensy_flash}"
BOARD="${BOARD:-auto}"
cd "$DIR"

install_loader() {
  if command -v teensy_loader_cli >/dev/null 2>&1; then
    return 0
  fi
  echo "installing teensy_loader_cli..."
  sudo apt-get update -qq
  if sudo apt-get install -y -qq teensy-loader-cli 2>/dev/null; then
    return 0
  fi
  # fallback: build from source
  sudo apt-get install -y -qq git build-essential libusb-dev || \
    sudo apt-get install -y -qq git build-essential libusb-1.0-0-dev
  rm -rf /tmp/teensy_loader_cli
  git clone --depth 1 https://github.com/PaulStoffregen/teensy_loader_cli.git /tmp/teensy_loader_cli
  make -C /tmp/teensy_loader_cli
  sudo cp /tmp/teensy_loader_cli/teensy_loader_cli /usr/local/bin/
}

install_loader
bash "$DIR/identify_teensy.sh" || true

pick_mcu() {
  case "$BOARD" in
    teensy32) echo "mk20dx256"; return ;;
    teensy40|teensy41) echo "imxrt1062"; return ;;
  esac
  # auto: prefer product string / known serial mode hints
  prod="$(cat /sys/bus/usb/devices/*/product 2>/dev/null | tr '\n' ' ' || true)"
  if echo "$prod" | grep -qi 'Teensy 4'; then
    echo "imxrt1062"
  elif echo "$prod" | grep -qi 'Teensy 3'; then
    echo "mk20dx256"
  else
    # Kendu Control Blok modules in the field are usually 3.2; try that first.
    echo "mk20dx256"
  fi
}

MCU="$(pick_mcu)"
case "$MCU" in
  mk20dx256) HEX="$DIR/firmware_teensy32.hex" ;;
  imxrt1062)
    if [[ "$BOARD" == "teensy41" ]]; then
      HEX="$DIR/firmware_teensy40.hex"
      # same imxrt core; use teensy40 build if no separate 41 hex
    else
      HEX="$DIR/firmware_teensy40.hex"
    fi
    ;;
  *) echo "unknown mcu $MCU"; exit 1 ;;
esac

echo "MCU=$MCU HEX=$HEX"
echo "Flashing (wait up to 60s). If stuck: press PROGRAM button on Teensy once."

# -w wait for device, -v verbose, -s soft reboot into bootloader when possible
set +e
teensy_loader_cli -w -v -s --mcu="$MCU" "$HEX"
rc=$?
set -e

if [[ $rc -ne 0 ]]; then
  echo
  echo "Flash failed (rc=$rc)."
  echo ">>> Bitte jetzt die PROGRAM-Taste am Teensy kurz druecken <<<"
  echo "Retrying 90s..."
  teensy_loader_cli -w -v --mcu="$MCU" "$HEX"
fi

echo "flash ok"
sleep 2
bash "$DIR/identify_teensy.sh" || true
