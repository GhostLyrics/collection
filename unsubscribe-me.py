#!/usr/bin/python

"""Easily unsubscribe from newsletters your former co-workers subscribed to."""

import argparse
import smtplib
import sys

from email.mime.text import MIMEText


def main():
    """Unsubscribe from unwanted newsletters as someone else."""

    options = parse_arguments()

    message = create_message(options)

    if not options.dry_run:
        send_mail(message)


def parse_arguments():
    """Parse given command line arguments."""

    text_dry_run = "Perform a dry run. Do not send out real mail."
    text_sender = "The e-mail address you want to send from."
    text_recipient = "The e-mail address you want to send to."

    parser = argparse.ArgumentParser()

    parser.add_argument("--dry-run", help=text_dry_run, action="store_true")
    parser.add_argument("-s", "--sender", help=text_sender, required=True)
    parser.add_argument("-r", "--recipient", help=text_recipient,
                        required=True)

    arguments = parser.parse_args()
    return arguments


def create_message(options):
    """Create the unsubscribe message."""

    message = MIMEText("Please unsubscribe me.")

    message['Subject'] = "UNSUBSCRIBE"

    if "@" not in options.sender or "@" not in options.recipient:
        sys.exit("Both recipient and sender need to be valid e-mail addresses")

    message['From'] = options.sender
    message['To'] = options.recipient

    if options.dry_run:
        print "Created message:\n"
        print message

    return message


def send_mail(message):
    """Send the created message."""

    connection = smtplib.SMTP()
    connection.connect()
    connection.sendmail(message['From'], message['To'],
                        message.as_string())

if __name__ == "__main__":
    main()
