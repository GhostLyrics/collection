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


def parse_arguments():
    """Parse given command line arguments."""

    text_verbose = "print detailed information about program flow"

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", help=text_verbose,
                        action="store_true")

    arguments = parser.parse_args()
    return arguments


def get_grub_list(options):
    """Get the list of all GRUB menu entries via grep."""

    command = ["grep", "--ignore-case", "menuentry '", "/boot/grub/grub.cfg"]

    if options.verbose is True:
        print "Will execute the following command:"
        print command

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
                print "Found the following line as Windows boot entry:"
                print windows_line

    if windows_line is not None:
        identifier = windows_line.split("'", 2)[1]

        if options.verbose is True:
            print "Will use the following identifier to supply to grub-reboot:"
            print identifier

    return identifier


def reboot_with(windows, options):
    """Use the given identifier for next reboot."""

    command = ["grub-reboot", windows]

    if options.verbose is True:
        print "Will execute the following command:"
        print command

    subprocess.call(command)

if __name__ == "__main__":
    main()
