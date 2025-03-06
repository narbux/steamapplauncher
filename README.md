# Gamelaunchers from Flatpak Steam for GNOME

This script runs on every login and copies the files from the Flatpak-version
of Steam to the correct locations for a Gnome desktop for them to appear in the
Gnome application launcher.

The script rewrites the `Exec=` line of the .desktop-files to account for
Flatpak. It also rewrites the `Icon=` line to match the correpsonding file in
the confined directory from Steam.

## Installation

- Copy `steamapplauncher.py` to $HOME/.local/bin
- Copy `steamapplauncher.service` and `steamapplauncher.timer` to
`$HOME/.config/systemd/user/`
- Execute `systemctl --user enable steamapplauncher.timer`
