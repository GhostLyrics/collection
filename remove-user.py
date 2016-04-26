#!/usr/bin/env python3

import argparse
import configparser
import logging
import logging.handlers
import os.path
import sys

def main():

    arguments = parse_arguments()
    log = create_logger(arguments)
    configuration = load_configuration(arguments.config)

    if configuration.getboolean("handlers", "gitlab"):
        log.info("GitLab module enabled.")


def create_logger(arguments):
    """Set up logging to stdout for user and syslog for audit trail."""

    if arguments.debug:
        debug = "[DEBUG: action not performed]"
    else:
        debug = ""

    # syslog section

    if sys.platform == "darwin":
        address = "/var/run/syslog"

    elif sys.platform == "linux2":
        address = "/dev/log"

    logger = logging.getLogger('Logger')
    facility = logging.handlers.SysLogHandler.LOG_USER
    syslog_handler = logging.handlers.SysLogHandler(address, facility)
    log_format = logging.Formatter('remove-user: {} %(message)s'.format(debug))

    syslog_handler.setFormatter(log_format)
    logger.addHandler(syslog_handler)
    logger.setLevel(logging.INFO)

    # stdout section

    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(formatter)

    if arguments.debug:
        stdout_handler.setLevel(logging.DEBUG)
    elif arguments.quiet:
        stdout_handler.setLevel(logging.ERROR)
    else:
        stdout_handler.setLevel(logging.WARNING)

    logger.addHandler(stdout_handler)

    return logger


def parse_arguments():


    text_configuration_file = "use this configuration file instead of default"
    text_debug = "run a simulation of all actions"
    text_quiet = "suppress non-critical output"

    parser = argparse.ArgumentParser()

    parser.add_argument("--config",
                        help=text_configuration_file,
                        default="~/.collection/remove-user.ini",
                        metavar="PATH")

    parser.add_argument("--debug",
                        help=text_debug,
                        action="store_true")

    parser.add_argument("--quiet",
                        help=text_quiet,
                        action="store_true")

    arguments = parser.parse_args()
    return arguments

def load_configuration(configuration_file):

    configuration = configparser.ConfigParser()
    configuration.read(os.path.expanduser(configuration_file))

    return configuration

if __name__ == "__main__":
    main()
