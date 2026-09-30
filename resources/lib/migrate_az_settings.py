# -*- coding: utf-8 -*-

import os
import shutil
import sys

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

TARGET_DATA = os.path.join(
    ADDON_DATA,
    TARGET_SKIN_ID
)

TARGET_SETTINGS = os.path.join(
    TARGET_DATA,
    "settings.xml"
)

AUTO_MIGRATION_MARKER = os.path.join(
    TARGET_DATA,
    ".az_settings_import_prompted"
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


def mark_auto_prompt_handled():
    try:
        ensure_parent(AUTO_MIGRATION_MARKER)

        with open(AUTO_MIGRATION_MARKER, "w") as marker:
            marker.write("1\n")

        log("Automatic migration prompt marked as handled.")
    except OSError as exc:
        log(
            "Unable to create automatic migration marker: {}".format(
                exc
            )
        )


def migrate(auto=False):
    mode = "automatic" if auto else "manual"

    log("{} migration started.".format(mode.capitalize()))

    if not os.path.isfile(SOURCE_SETTINGS):
        if auto:
            log(
                "Automatic migration skipped: original skin settings "
                "were not found."
            )
        else:
            xbmcgui.Dialog().ok(
                "Import Arctic: Zephyr - Reloaded Settings",
                "No settings from the original Arctic: Zephyr - Reloaded "
                "skin were found."
            )
            log(
                "Manual migration stopped: original skin settings "
                "not found."
            )
        return

    if auto and os.path.isfile(AUTO_MIGRATION_MARKER):
        log(
            "Automatic migration skipped: migration prompt was "
            "already handled."
        )
        return

    confirmed = xbmcgui.Dialog().yesno(
        "Import Arctic: Zephyr - Reloaded Settings",
        "Existing settings from Arctic: Zephyr - Reloaded were found.\n\n"
        "Would you like to import them into the AKL Edition?\n\n"
        "This will replace the current AKL Edition skin settings and "
        "home-screen widget configuration."
    )

    if auto:
        mark_auto_prompt_handled()

    if not confirmed:
        log("{} migration cancelled by user.".format(mode.capitalize()))
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
            log(
                "Removed AKL Skin Shortcuts hash to force rebuild."
            )
        except OSError as exc:
            log(
                "Unable to remove Skin Shortcuts hash: {}".format(
                    exc
                )
            )

    if settings_copied and properties_copied:
        message = (
            "Your Arctic: Zephyr - Reloaded settings and home-screen "
            "configuration were imported successfully.\n\n"
            "Reload the skin to apply the imported settings."
        )
    elif settings_copied:
        message = (
            "The skin settings were imported successfully. No saved "
            "home-screen widget configuration was found for Arctic: "
            "Zephyr - Reloaded, so widgets were not changed."
        )
    else:
        message = "The settings could not be imported."

    xbmcgui.Dialog().ok(
        "Arctic: Zephyr - Reloaded (AKL Edition)",
        message
    )

    log("{} migration finished.".format(mode.capitalize()))


if __name__ == "__main__":
    auto_mode = (
        len(sys.argv) > 1 and
        sys.argv[1].lower() == "auto"
    )

    migrate(auto=auto_mode)
