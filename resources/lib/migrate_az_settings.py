# -*- coding: utf-8 -*-

import os
import shutil

import xbmc
import xbmcgui
import xbmcvfs


SOURCE_SKIN_ID = "skin.arctic.zephyr.mod"
TARGET_SKIN_ID = "skin.arctic.zephyr.akl"

PROFILE = xbmcvfs.translatePath("special://profile")
ADDON_DATA = os.path.join(PROFILE, "addon_data")
SKIN_SHORTCUTS_DATA = os.path.join(ADDON_DATA, "script.skinshortcuts")

SOURCE_SETTINGS = os.path.join(
    ADDON_DATA,
    SOURCE_SKIN_ID,
    "settings.xml"
)

TARGET_SETTINGS = os.path.join(
    ADDON_DATA,
    TARGET_SKIN_ID,
    "settings.xml"
)

SOURCE_PROPERTIES = os.path.join(
    SKIN_SHORTCUTS_DATA,
    SOURCE_SKIN_ID + ".properties"
)

TARGET_PROPERTIES = os.path.join(
    SKIN_SHORTCUTS_DATA,
    TARGET_SKIN_ID + ".properties"
)

TARGET_HASH = os.path.join(
    SKIN_SHORTCUTS_DATA,
    TARGET_SKIN_ID + ".hash"
)


def log(message):
    xbmc.log(
        "[Arctic Zephyr AKL Migration] {}".format(message),
        xbmc.LOGINFO
    )


def ensure_parent(path):
    parent = os.path.dirname(path)
    if not os.path.isdir(parent):
        os.makedirs(parent)


def copy_file(source, target, description):
    if not os.path.isfile(source):
        log("{} not found: {}".format(description, source))
        return False

    ensure_parent(target)
    shutil.copy2(source, target)

    log(
        "Copied {}: {} -> {}".format(
            description,
            source,
            target
        )
    )
    return True


def migrate():
    log("Migration started.")

    if not os.path.isfile(SOURCE_SETTINGS):
        xbmcgui.Dialog().ok(
            "Import Arctic: Zephyr - Reloaded Settings",
            "No settings from the original Arctic: Zephyr - Reloaded skin were found."
        )
        log("Migration stopped: original skin settings not found.")
        return

    if not xbmcgui.Dialog().yesno(
        "Import Arctic: Zephyr - Reloaded Settings",
        "Import your settings from Arctic: Zephyr - Reloaded into the AKL Edition?\n\n"
        "This will replace the current AKL Edition skin settings and home-screen "
        "widget configuration."
    ):
        log("Migration cancelled by user.")
        return

    settings_copied = copy_file(
        SOURCE_SETTINGS,
        TARGET_SETTINGS,
        "skin settings"
    )

    properties_copied = copy_file(
        SOURCE_PROPERTIES,
        TARGET_PROPERTIES,
        "Skin Shortcuts properties"
    )

    if properties_copied and os.path.isfile(TARGET_HASH):
        try:
            os.remove(TARGET_HASH)
            log("Removed AKL Skin Shortcuts hash to force rebuild.")
        except OSError as exc:
            log("Unable to remove Skin Shortcuts hash: {}".format(exc))

    if settings_copied and properties_copied:
        message = (
            "Your Arctic: Zephyr - Reloaded settings and home-screen "
            "configuration were imported successfully.\n\n"
            "Reload the skin to apply the imported settings."
        )
    elif settings_copied:
        message = (
            "The skin settings were imported successfully. No saved home-screen "
            "widget configuration was found for Arctic: Zephyr - Reloaded, so "
            "widgets were not changed."
        )
    else:
        message = "The settings could not be imported."

    xbmcgui.Dialog().ok(
        "Arctic: Zephyr - Reloaded (AKL Edition)",
        message
    )

    log("Migration finished.")


if __name__ == "__main__":
    migrate()
