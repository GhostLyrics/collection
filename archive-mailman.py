#!/usr/bin/env python

"""
Archive and delete a mailman mailing list.

Lists are deleted with the mailman provided `rmlist` interface.
Allows to perform a --dry-run.

Depends on mailman's `rmlist`.
"""

import argparse
import logging
import logging.handlers
import os.path
import subprocess
import sys


def main():
    """Archive and delete a mailman mailing list."""

    options = parse_arguments()
    log = create_logger(options)

    archive_list(options, log)
    remove_list(options, log)


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
    log_format = logging.Formatter('archive-mailman: %(message)s')
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


def parse_arguments():
    """Parse given command line arguments."""

    text_dry_run = "run in simulated mode and only print actions"
    text_verbose = "display messages about program flow"
    text_listname = "the mailman mailing list to archive and remove"
    text_listpath = "the path to the mailman folder"

    parser = argparse.ArgumentParser()

    parser.add_argument("listname", help=text_listname)
    parser.add_argument("-d", "--dry-run", help=text_dry_run,
                        action="store_true")
    parser.add_argument("-v", "--verbose", help=text_verbose,
                        action="store_true")
    parser.add_argument("-p", "--archives-path", help=text_listpath,
                        metavar="PATH")

    arguments = parser.parse_args()
    return arguments


def archive_list(options, log):
    """Archive the specified mailing list's directory."""

    if options.archives_path is None:
        # default list path if not specified otherwise
        list_path = os.path.join("/var/lib/mailman/archives/private",
                                 options.listname)
    else:
        list_path = os.path.join(options.archives_path, options.listname)

    tar_command = ["tar", "czpvf", "{}.tar.gz".format(options.listname),
                   list_path]

    try:
        if options.dry_run is True:
            log.info("Command to execute: {}".format(tar_command))

        else:
            log.info("Starting archival of mailing list \"{}\".".format(
                options.listname))
            output = subprocess.check_output(tar_command,
                                             stderr=subprocess.STDOUT)
            return output

    except subprocess.CalledProcessError, error:

        error_message = "Could not complete archival process."

        log.error("{} Error was: {}".format(error_message, error))
        sys.exit("{} Error was: {}".format(error_message, error))


def remove_list(options, log):
    """Use mailman tools to remove the specified mailing list."""

    command = ["rmlist", "--archives", options.listname]

    if options.dry_run is True:
        log.info("Command to execute: {}".format(command))

    else:
        try:
            subprocess.check_output(command)
            log.info("Deleted list \"{}\".".format(options.listname))
        except subprocess.CalledProcessError:
            log.error("Deletion of list \"{}\" failed.".format(
                options.listname))
            sys.exit("Aborted.")


if __name__ == "__main__":
    main()
