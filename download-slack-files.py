#!/usr/bin/env python

# Allow CAPS in function names
# pylint: disable=C0103

"""
Download all files linked in a Slack export archive.

All uploaded files are downloaded into their respective channel folders.
Optionally, Slack IDs can be used instead of file names.

"""

import argparse
from functools import partial
import json
import os.path
from multiprocessing import Pool
import urllib2
import sys

def find_directories(root_directory):
    """Return a list of subdirectories prefixed with the parent directory."""

    search_directories = []

    if os.path.isdir(root_directory):
        files_and_folders = os.listdir(root_directory)
        for item in files_and_folders:
            sub_directory = os.path.join(root_directory, item)
            if os.path.isdir(sub_directory):
                search_directories.append(sub_directory)
        return search_directories

    else:
        sys.exit("Error: {} is not a valid directory".format(root_directory))

def find_URLs(directory, options):
    """Find URLs in JSON files."""

    files = os.listdir(directory)
    filtered_files = []
    files_for_download = []
    for item in files:
        if item.endswith(".json"):
            filtered_files.append(item)

    for item in filtered_files:
        file_path = os.path.join(directory, item)

        with open(file_path, "r") as json_file:
            payload = json.load(json_file)
            for message in payload:
                if ("subtype" in message
                    and message.get("subtype") == "file_share"):

                    download_URL = message.get("file").get("url_download")

                    if options.remote_name:
                        download_filename = message.get("file").get("id")
                    else:
                        download_filename = message.get("file").get("name")
                        if download_filename.startswith("-."):
                            download_filename = download_filename.lstrip("-")
                            download_filename = "{}{}".format(
                                message.get("file").get("id"), download_filename)

                    files_for_download.append((download_filename, download_URL))

    download_URLs(files_for_download, directory)

def download_URLs(files_for_download, directory):
    """Download the files."""

    for pair in files_for_download:
        path = os.path.join(directory, pair[0])
        download = urllib2.urlopen(pair[1])

        content = download.read()

        with open(path, "wb") as downloaded_file:
            downloaded_file.write(content)

def parse_arguments():
    """Parse given command line arguments."""

    text_folder = "the unzipped Slack export directory"
    text_remote_name = "keep Slack file IDs instead of using the file names"

    parser = argparse.ArgumentParser()

    parser.add_argument("folder", help=text_folder)
    parser.add_argument("--remote-name", help=text_remote_name,
        action="store_true")

    arguments = parser.parse_args()
    return arguments

def main():
    """Download all files linked in a Slack export archive."""

    options = parse_arguments()

    directories = find_directories(options.folder)
    process_pool = Pool(len(directories))

    function_call = partial(find_URLs, options=options)

    process_pool.map(function_call, directories)

if __name__ == "__main__":
    main()
