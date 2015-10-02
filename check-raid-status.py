#!/usr/bin/env python

"""
Check RAID controller for health information, write to syslog.

Works with controllers of type MegaRAID and 3ware.
Shows progress while rebuilding. Allows checking of multiple controllers.

Depends on the vendor specific binaries for MegaRAID (storcli64) and 3ware
(tw_cli) being installed and in the PATH.
"""

import argparse
import logging
import logging.handlers
import socket
import subprocess
import sys


def parse_arguments():
    """Parse given command line arguments."""

    text_type = "type of RAID controller (supported: MegaRAID or 3ware)"
    text_controller = "number of RAID controller"
    text_cron = "complain about drive issues to stdout"

    parser = argparse.ArgumentParser()

    parser.add_argument("type", help=text_type)
    parser.add_argument("controller", help=text_controller, nargs='+',
                        type=int)
    parser.add_argument("--cron-mode", help=text_cron, action="store_true")

    arguments = parser.parse_args()
    return arguments


def main():
    """Check RAID controller for health information."""

    options = parse_arguments()
    log = create_logger()

    hostname = socket.gethostname()
    log.info("Running RAID check on %s", hostname)

    for controller in options.controller:
        command = build_command(options.type, controller, log)

        try:
            command_result = subprocess.check_output(command,
                                                     stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, error:
            log_and_quit("Checking controller failed.", log, error)
        except OSError, error:
            log_and_quit("Vendor binary not found in PATH.", log, error)

        message = "All is well and all shall be well."
        issue_detected = False

        lines = command_result.split("\n")

        for line in lines:
            if not line == '':

                if options.type == "3ware":
                    result = handle_3ware(line, log, controller)

                elif options.type == "MegaRAID":
                    result = handle_megaraid(line, log, controller)

                if result is False:
                    message = "RAID status problematic."
                    issue_detected = True

        if issue_detected is True and options.cron_mode is True:
            print message
            print command_result

        log.info("Check completed for controller %s. %s", controller, message)


def build_command(controller_type, controller_number, log):
    """Build shell command to run according to model and controller number."""

    if controller_type == "MegaRAID":
        command = ["storcli64", "/c{}".format(controller_number), "show"]
    elif controller_type == "3ware":
        command = ["tw_cli", "info", "c{}".format(controller_number)]
    else:
        log_and_quit("Controller type unknown.", log)

    return command


def log_and_quit(message, log, error=None):
    """Write error message to log and quit."""

    if error is not None:
        log.error("{} Error was: {}".format(message, error))
        sys.exit("{} Error was: {}".format(message, error))
    else:
        log.error("{}".format(message))
        sys.exit("{}".format(message))


def handle_megaraid(line, log, controller):
    """Start the pipeline for MegaRAID type information."""

    if line.startswith(" {0} {0}".format(controller)):
        return report_megaraid(line, log, controller)


def report_megaraid(line, log, controller):
    """Report findings in MegaRAID pipeline, return BOOL of health check."""

    success = True
    progress = None
    data_type = None

    details = line.split()
    status = details[6]

    if details[5] == "DRIVE":
        data_type = "Drive"
        unit = details[2]
    else:
        data_type = "Unit"
        unit = details[1]

    # give warning if something is not perfectly well
    # Onln: Online | Optl: Optimal | Rbld: Rebuilding
    if status not in ["Onln", "Optl", "Rbld"]:
        success = False

    if progress is None:
        log.info("Controller: {}, {} {}: Status: {}".format(
            controller, data_type, unit, status))
    else:
        # TODO: progress indication
        pass

    return success


def handle_3ware(line, log, controller):
    """Start the pipeline for 3ware type information."""

    if line[0] == "u" or line[0] == "p":
        return report_3ware(line, log, controller)


def report_3ware(line, log, controller):
    """Report findings in 3ware pipeline, return BOOL of health check."""

    success = True
    progress = None
    data_type = None

    if line[0] == "u":
        data_type = "Unit"
        status = line.split()[2]
        if status == "REBUILDING":
            progress = line.split()[3]

    elif line[0] == "p":
        data_type = "Drive"
        status = line.split()[1]

    # give warning if something is not perfectly well
    if status not in ["OK", "REBUILDING", "VERIFYING"]:
        success = False

    if progress is None:
        log.info("Controller: {}, {} {}: Status: {}".format(
            controller, data_type, line[1], status))
    else:
        log.info("Controller: {}, {} {}: Status: {}, Completion: {}".format(
            controller, data_type, line[1], status, progress))

    return success


def create_logger():
    """Set up global logging."""

    logger = logging.getLogger('Logger')
    address = '/dev/log'  # Note: Linux specific
    facility = logging.handlers.SysLogHandler.LOG_USER
    handler = logging.handlers.SysLogHandler(address, facility)
    log_format = logging.Formatter('RAID check: %(message)s')
    handler.setFormatter(log_format)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


if __name__ == '__main__':
    main()
