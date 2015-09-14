#!/usr/bin/env python

"""
Check RAID controller for health information, write to syslog.

Can work with controllers of type MegaRAID and 3ware.
Shows progress while rebuilding.

"""

import socket
import subprocess
import logging
import logging.handlers


def get_configuration():
    """Return map containing commands to run and parser information."""

    # structure:
    # hostname: list(tuple(list(command, arguments), parser), ...)
    # this allows for multiple RAIDs per host

    command_map = {
        "dummy1":     [(["/usr/3ware/tw_cli", "info", "c4"], "3ware")],
        "dummy2":     [(["storcli64", "/c0", "show"], "MegaRAID")],
        "dummy3":     [(["/usr/3Ware/tw_cli", "info", "c0"], "3ware"),
                       (["/usr/3Ware/tw_cli", "info", "c5"], "3ware")],
        "dummy4":     [(["storcli64", "/c0", "show"], "MegaRAID")],
        "dummy5":     [(["/usr/3ware/tw_cli", "show", "c4"], "3ware")],
        "dummy6":     [(["tw_cli", "show", "c4"], "3ware")],
        "dummy7":     [(["tw_cli", "show", "c4"], "3ware")],
        "dummy8":     [(["storcli64", "/c0", "show"], "MegaRAID")]
        }

    return command_map


def main():
    """Check RAID controller for health information."""

    log = create_logger()

    hostname = socket.gethostname()
    log.info("Running RAID check on %s", hostname)

    try:
        configuration = get_configuration().get(hostname)
    except KeyError:
        log.error("RAID check not configured for %s", hostname)

    for instruction in configuration:
        command_result = subprocess.check_output(instruction[0])
        message = "No issues detected."

        lines = command_result.split("\n")

        for line in lines:
            if not line == '':
                if instruction[1] == "3ware":

                    controller = instruction[0][2][1]
                    result = handle_3ware(line, log, controller)

                elif instruction[1] == "MegaRAID":

                    controller = instruction[0][1][2]
                    result = handle_megaraid(line, log, controller)

                if result is False:
                    message = "RAID status problematic."

        log.info("Check completed for controller %s. %s", controller, message)


def handle_megaraid(line, log, controller):
    """Start the pipeline for MegaRAID type information."""

    if line.startswith(" {0} {0}".format(controller)):
        return report_megaraid(line, log, controller)


def report_megaraid(line, log, controller):
    """Report findings in MegaRAID pipeline."""

    success = True

    details = line.split()
    status = details[6]

    if details[5] == "DRIVE":
        data_type = "Drive"
        unit = details[2]
    else:
        data_type = "Unit"
        unit = details[1]

    # give warning if something is not perfectly well
    if status != "Onln" and status != "Optl":
        success = False

    log.info("Controller: {}, {} {}: Status: {}".format(
        controller, data_type, unit, status))

    return success


def handle_3ware(line, log, controller):
    """Start the pipeline for 3ware type information."""

    if line[0] == "u" or line[0] == "p":
        return report_3ware(line, log, controller)


def report_3ware(line, log, controller):
    """Report findings in 3ware pipeline, return with bool of health check."""

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
    if status != "OK" and status != "REBUILDING":
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
