#!/usr/bin/env python

# Allow CAPS in function names
# pylint: disable=C0103

"""
Archive and remove a user's home directory.

Home directories are moved to trash instead of deleted immediately.
If SSH keys are archived the user is notified.
Allows to perform a --dry-run.
"""

import argparse
import logging
import logging.handlers
import os.path
import subprocess
import sys

def main():
    """Archive and remove a user's home directory."""

    options = parse_arguments()
    log = create_logger(options)

    archive_output = archive_home(options, log)
    check_for_SSH_keys(archive_output, options, log)
    trash_home(options, log)

def create_logger(options):
    """Set up global logging."""

    # syslog section

    if sys.platform == "darwin":
        address = "/var/run/syslog"

    elif sys.platform == "linux2":
        address = "/dev/log"

    logger = logging.getLogger('Logger')
    facility = logging.handlers.SysLogHandler.LOG_USER
    handler = logging.handlers.SysLogHandler(address, facility)
    log_format = logging.Formatter('archive-home: %(message)s')
    handler.setFormatter(log_format)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # stdout section

    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(formatter)

    if options.verbose or options.dry_run:
        stdout_handler.setLevel(logging.INFO)
    else:
        stdout_handler.setLevel(logging.WARNING)

    logger.addHandler(stdout_handler)

    return logger


def check_for_SSH_keys(archive_output, options, log):
    """Notify if authorized SSH key files have been archived."""

    if options.dry_run == True:
        log.info("SSH Keys would be checked here.")

    else:
        if "authorized_keys" in archive_output:
            log.warn("SSH keys archived.")


def parse_arguments():
    """Parse given command line arguments."""

    text_username = "the user whose home directory should be archived"
    text_dry_run = "run in simulated mode and only print actions"
    text_verbose = "display messages about program flow"

    parser = argparse.ArgumentParser()

    parser.add_argument("user", help=text_username)
    parser.add_argument("-d", "--dry-run", help=text_dry_run,
                        action="store_true")
    parser.add_argument("-v", "--verbose", help=text_verbose,
                        action="store_true")

    arguments = parser.parse_args()
    return arguments


def archive_home(options, log):
    """Archive the specified user's home directory."""

    home = os.path.expanduser("~{}".format(options.user))
    tar_command = ["tar", "czpvf", "{}.tar.gz".format(options.user), home]

    try:
        if options.dry_run == True:
            log.info("Command to execute: {}".format(tar_command))

        else:
            log.info("Starting archival of home for user {}.".format(
                options.user))
            output = subprocess.check_output(tar_command,
                                             stderr=subprocess.STDOUT)
            return output

    except subprocess.CalledProcessError, error:

        error_message = "Could not complete archival process."

        log.error("{} Error was: {}".format(error_message, error))
        sys.exit("{} Error was: {}".format(error_message, error))


def trash_home(options, log):
    """Move the specified user's home directory into the trash."""

    if sys.platform == "darwin":
        trash_alias = "trash"

    elif sys.platform == "linux2":
        trash_alias = "trash-put"

    home = os.path.expanduser("~{}".format(options.user))

    trash_command = [trash_alias, home]

    if options.dry_run == True:
        log.info("Command to execute: {}".format(trash_command))

    else:
        try:
            subprocess.check_output(trash_command)
            log.info("Moved home of {} to trash.".format(options.user))
        except Exception:
            log.error("Moving home of {} to trash failed.".format(options.user))
            sys.exit("Aborted.")


if __name__ == "__main__":
    main()
