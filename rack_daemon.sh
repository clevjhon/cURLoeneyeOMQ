#!/usr/bin/env bash
INTERVAL=60 # Execution interval in seconds

while true; do
    ~/init_rack.sh >> "$HOME/oeneye_daemon.log" 2>&1
    sleep "$INTERVAL"
done
