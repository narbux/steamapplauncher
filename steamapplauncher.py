#!/usr/bin/env python3
"""
1. make list of all files in the steam dir
2. check if files are present in launcher dir
3. if not present: change 'exec' line to add flatpak execution command
4. save file to applications dir in $HOME.local/share/
"""

import logging
from logging.handlers import RotatingFileHandler
import re
import shutil
import subprocess
import sys
from pathlib import Path

STEAM_FLATPAK_DIR = (
    Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/applications"
)
STEAM_ICON_DIR = (
    Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/icons/hicolor/"
)

APPLAUNCHER_DIR = Path.home() / ".local/share/applications"
EXCLUDE_LIST = ["Proton", "Steam Linux Runtime"]
FLATPAK_EXEC = "Exec=flatpak run com.valvesoftware.Steam :steam steam"

STEAM_FILES: list[Path] = []


def sanitize_directory_list() -> list[Path]:
    if not STEAM_FLATPAK_DIR.exists() or not STEAM_FLATPAK_DIR.is_dir():
        raise FileNotFoundError(
            f"{STEAM_FLATPAK_DIR} does not exist or isn't a directory"
        )
    dir_listing = list(STEAM_FLATPAK_DIR.iterdir())
    logger.debug(f"Dirty Steam directory listing: {dir_listing}")
    steam_dir = [
        file
        for file in dir_listing
        if not any(exclusion in file.name for exclusion in EXCLUDE_LIST)
    ]
    logger.debug(f"Sanitized Steam directory listing: {steam_dir}")
    return steam_dir


def copy_files(source_dir: list[Path]) -> None:
    existing_files = list(APPLAUNCHER_DIR.iterdir())
    copied_files_counter = 0
    for file in source_dir:
        if file in existing_files:
            logger.warning(f"{file.name} already in target directory, skipping")
            continue
        if file.is_dir():
            logger.warning(f"<{file.name}> is a directory, skipping")
            continue
        logger.debug(f"Copying {file.name}")
        shutil.copyfile(file, APPLAUNCHER_DIR / file.name, follow_symlinks=False)
        STEAM_FILES.append(Path(APPLAUNCHER_DIR / file.name))
        copied_files_counter += 1
    logger.info(f"Copied {copied_files_counter} files")


def rewrite_desktop_file() -> None:
    for file in STEAM_FILES:
        logger.debug(f"Rewriting exec line in {file.name}")
        with open(file, "r") as source:
            lines = source.readlines()
        with open(file, "w") as destination:
            for line in lines:
                destination.write(re.sub(r"Exec=steam steam", FLATPAK_EXEC, line))

        logger.debug(f"Rewriting icon line in {file.name}")
        app_id_number = 0
        with open(file, "r") as source:
            lines = source.readlines()

        for line in lines:
            if line.startswith("Icon="):
                app_id_number = line.split("_")[-1].strip()
                logger.debug(f"Found app_id_number for {file.name}: {app_id_number}")

        if (STEAM_ICON_DIR / f"256x256/apps/steam_icon_{app_id_number}.png").exists():
            icon_uri = STEAM_ICON_DIR / f"256x256/apps/steam_icon_{app_id_number}.png"
        elif (STEAM_ICON_DIR / f"192x192/apps/steam_icon_{app_id_number}.png").exists():
            icon_uri = STEAM_ICON_DIR / f"192x192/apps/steam_icon_{app_id_number}.png"
        elif (STEAM_ICON_DIR / f"128x128/apps/steam_icon_{app_id_number}.png").exists():
            icon_uri = STEAM_ICON_DIR / f"128x128/apps/steam_icon_{app_id_number}.png"
        elif (STEAM_ICON_DIR / f"96x96/apps/steam_icon_{app_id_number}.png").exists():
            icon_uri = STEAM_ICON_DIR / f"96x96/apps/steam_icon_{app_id_number}.png"
        elif (STEAM_ICON_DIR / f"64x64/apps/steam_icon_{app_id_number}.png").exists():
            icon_uri = STEAM_ICON_DIR / f"64x64/apps/steam_icon_{app_id_number}.png"
        else:
            icon_uri = STEAM_ICON_DIR / f"32x32/apps/steam_icon_{app_id_number}.png"
        logger.debug(f"{icon_uri=}")

        with open(file, "w") as destination:
            for line in lines:
                if line.startswith("Icon="):
                    destination.write(f"Icon={icon_uri}\n")
                else:
                    destination.write(line)


def reload_gtk_cache() -> None:
    logger.debug("Reloading GTK icon cache")
    subprocess.run(["gtk-update-icon-cache"])


def main() -> None:
    logger.info("Application started")
    steam_dir = sanitize_directory_list()
    copy_files(steam_dir)
    rewrite_desktop_file()
    logger.debug(f"Final target directory listing: {list(APPLAUNCHER_DIR.iterdir())}")
    reload_gtk_cache()
    logger.info("Application finished")


def setup_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    log_file_handler = RotatingFileHandler(
        Path.home() / ".cache/steamapplauncher.log",
        mode="a",
        encoding="UTF-8",
        maxBytes=262100,
        backupCount=0,
    )
    log_file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)-8s [%(module)s/%(lineno)s] :: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    log_file_handler.setLevel(logging.DEBUG)
    log_stream_handler = logging.StreamHandler(stream=sys.stdout)
    log_stream_handler.setFormatter(logging.Formatter("%(message)s"))
    log_stream_handler.setLevel(logging.INFO)
    logger.addHandler(log_file_handler)
    logger.addHandler(log_stream_handler)
    return logger


if __name__ == "__main__":
    logger = setup_logger()
    main()
