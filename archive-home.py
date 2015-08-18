#!/usr/bin/env python

# Allow CAPS in function names
# pylint: disable=C0103

"""
Archive and remove a user's home directory.

Notify if SSH keys are archived.
Allows to perform a --dry-run.
"""

import argparse
import os.path
import subprocess
import sys

def main():
    """Archive and remove a user's home directory."""

    options = parse_arguments()

    archive_output = archive_home(options)
    check_for_SSH_keys(archive_output, options)
    trash_home(options)

    print "Done."


def check_for_SSH_keys(archive_output, options):
    """Notify if authorized SSH key files have been archived."""

    if options.dry_run == True:
        print "SSH Keys would be checked here."

    else:
        if "authorized_keys" in archive_output:
            print "SSH keys archived."


def parse_arguments():
    """Parse given command line arguments."""

    text_username = "the user whose home directory should be archived"
    text_dry_run = "run in simulated mode and only print actions"

    parser = argparse.ArgumentParser()

    parser.add_argument("user", help=text_username)
    parser.add_argument("-d", "--dry-run", help=text_dry_run,
                        action="store_true")

    arguments = parser.parse_args()
    return arguments


def archive_home(options):
    """Archive the specified user's home directory."""

    home = os.path.expanduser("~{}".format(options.user))
    tar_command = ["tar", "czpvf", "{}.tar.gz".format(options.user), home]

    try:
        if options.dry_run == True:
            print "Command to execute:",
            print tar_command

        else:
            output = subprocess.check_output(tar_command,
                                             stderr=subprocess.STDOUT)
            return output

    except subprocess.CalledProcessError, error:
        print error
        sys.exit("Could not complete archival process.")


def trash_home(options):
    """Move the specified user's home directory into the trash."""

    if sys.platform == "darwin":
        trash_alias = "trash"

    elif sys.platform == "linux2":
        trash_alias = "trash-put"

    home = os.path.expanduser("~{}".format(options.user))

    trash_command = [trash_alias, home]

    if options.dry_run == True:
        print "Command to execute:",
        print trash_command

    else:
        subprocess.check_output(trash_command)


if __name__ == "__main__":
    main()
