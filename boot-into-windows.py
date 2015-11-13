#!/usr/bin/env python

"""
Boot into your Windows partition on next reboot.

Requires `GRUB_DEFAULT=saved` to be present in `/etc/default/grub`.
After changes to said file `(sudo) update-grub` must be run once.
"""

import subprocess


def main():
    """Boot into your Windows partition on next reboot."""

    entries = get_grub_list()
    windows = filter_grub_list(entries)
    reboot_with(windows)


def get_grub_list():
    """Get the list of all GRUB menu entries via grep."""

    command = ["grep", "--ignore-case", "menuentry '", "/boot/grub/grub.cfg"]
    result = subprocess.check_output(command)

    return result


def filter_grub_list(all_entries):
    """Get the Windows entry from the grub menuentries."""

    windows_line = None
    lines = all_entries.splitlines()

    for line in lines:
        if "Windows Boot Manager" in line:
            windows_line = line

    if windows_line is not None:
        identifier = windows_line.split("'", 2)[1]

    return identifier


def reboot_with(windows):
    """Use the given identifier for next reboot."""

    command = ["grub-reboot", windows]
    subprocess.call(command)

if __name__ == "__main__":
    main()
