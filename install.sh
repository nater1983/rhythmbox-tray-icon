#!/usr/bin/env bash

home_prefix="$HOME/.local/share/rhythmbox/plugins/tray_icon/"

mkdir -p $home_prefix
cp -u tray_icon.py tray_icon.plugin tray_playing.png tray_stopped.png $home_prefix
