#!/usr/bin/env python

"""
Boot into your Windows partition on next reboot.

Requires `GRUB_DEFAULT=saved` to be present in `/etc/default/grub`.
After changes to said file `(sudo) update-grub` must be run once.
"""

import argparse
import subprocess


def main():
    """Boot into your Windows partition on next reboot."""

    options = parse_arguments()

    entries = get_grub_list(options)
    windows = filter_grub_list(entries, options)
    reboot_with(windows, options)
    reboot(options)


def parse_arguments():
    """Parse given command line arguments."""

    text_verbose = "print detailed information about program flow"

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", help=text_verbose,
                        action="store_true")

    arguments = parser.parse_args()
    return arguments


def pretty_print(information_type, text, variable=None):
    """Print nicer verbose text."""

    if variable is None:
        string = "[{}]: <{}>".format(information_type.upper(), text)
    else:
        string = "[{}]: {} has the value: <{}>".format(
            information_type.upper(), variable, text)

    print string


def get_grub_list(options):
    """Get the list of all GRUB menu entries via grep."""

    command = ["grep", "--ignore-case", "menuentry '", "/boot/grub/grub.cfg"]

    if options.verbose is True:
        pretty_print("command", command)

    result = subprocess.check_output(command)

    return result


def filter_grub_list(all_entries, options):
    """Get the Windows entry from the grub menuentries."""

    windows_line = None
    lines = all_entries.splitlines()

    for line in lines:
        if "Windows Boot Manager" in line:
            windows_line = line

            if options.verbose is True:
                pretty_print("data", windows_line, "windows_line")

    if windows_line is not None:
        identifier = windows_line.split("'", 2)[1]

        if options.verbose is True:
            pretty_print("data", identifier, "identifier")

    return identifier


def reboot_with(windows, options):
    """Use the given identifier for next reboot."""

    command = ["grub-reboot", windows]

    if options.verbose is True:
        pretty_print("command", command)

    subprocess.check_call(command)


def reboot(options):
    """Execute reboot command."""

    command = ["reboot", "now"]

    if options.verbose is True:
        pretty_print("command", command)

    subprocess.call(command)

if __name__ == "__main__":
    main()
