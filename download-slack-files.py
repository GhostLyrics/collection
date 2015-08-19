#!/usr/bin/env python

"""Download all files linked in a Slack export archive."""

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

def find_URLs(directory):
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
                    download_filename = message.get("file").get("name")
                    download_URL = message.get("file").get("url_download")

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

def main():
    """Download all files linked in a Slack export archive."""

    if len(sys.argv) != 2:
        sys.exit("USAGE: slackdownload.py SLACK_EXPORT_DIRECTORY")

    else:
        root = sys.argv[1]
        directories = find_directories(root)
        process_pool = Pool(len(directories))
        process_pool.map(find_URLs, directories)

if __name__ == "__main__":
    main()
