# Gamelaunchers from Flatpak Steam for GNOME

This script runs on every time the flatpak Steam applications directory
is changed and copies the files from the Flatpak-version of Steam to the
correct locations for a Gnome desktop for them to appear in the Gnome
application launcher.

The script rewrites the `Exec=` line of the .desktop-files to account for
Flatpak. It also rewrites the `Icon=` line to match the correpsonding file in
the confined directory from Steam.

## Installation

To install, clone this directory and run the following commands:
```bash
mkdir -p $HOME/.local/bin $HOME/.config/systemd/user
cp steamapplauncher.py $HOME/.local/bin
cp steamapplauncher.service steamapplauncher.path $HOME/.config/systemd/user
systemctl --user enable steamapplauncher.path
```
