#!/usr/bin/env python

# Allow CAPS in function names
# pylint: disable=C0103

"""
Export posts and pages from Wordpress MySQL database to text files.

Auto-drafts are not exported.
Allows to use a non standard prefix for Wordpress tables.

Depends on MySQLdb module.
"""

import argparse
import getpass
import os
import os.path
import sys

# non standard modules
import MySQLdb as mdb

def main():
    """Export posts and pages from Wordpress MySQL database to text files."""

    options = parse_arguments()
    connection = None

    try:
        connection = connect(options)
        authors = get_authors(connection, options.prefix)
        posts = get_content(connection, "posts", options.prefix)
        pages = get_content(connection, "pages", options.prefix)

        if not options.include_categories and not options.include_tags:
            connection.close()

        if posts:
            export_content(posts, "posts", authors, options, connection)
        if pages:
            export_content(pages, "pages", authors, options, connection)

    except mdb.Error, error:
        sys.exit("Error: {}".format(error))

    finally:
        if connection:
            connection.close()

def export_content(content, content_type, authors, options, connection=None):
    """Write the exported content to files."""

    if os.path.exists("./{}".format(content_type)) is False:
        os.mkdir(content_type)

    exported_authors = None
    exported_tags = None
    exported_categories = None

    for entry in content:

        if options.include_author:
            exported_authors = authors

        if (options.include_categories or options.include_tags) and connection:
            labels = get_labels(entry, options.prefix, connection)

            if options.include_categories:
                exported_categories = labels.get("category")
            if options.include_tags:
                exported_tags = labels.get("post_tag")

        export = build_export(entry, options, exported_authors, exported_tags,
            exported_categories)

        with open(os.path.join(content_type, entry["post_name"])
                  + ".txt", "w") as textfile:
            textfile.write(export)

def get_labels(entry, prefix, connection):

    labels = {}

    statement = ("SELECT term_taxonomy_id FROM {}_term_relationships "
                 "WHERE object_id = {}".format(prefix, entry["ID"]))

    cursor = connection.cursor(mdb.cursors.DictCursor)


    cursor.execute(statement)
    unresolved_labels = cursor.fetchall()

    for label in unresolved_labels:

        statement = ("SELECT name from {}_terms where term_id "
                     "= {}".format(prefix, label.get("term_taxonomy_id")))
        cursor.execute(statement)
        result = cursor.fetchall()
        try:
            label_name = result[0].get("name")

        # there is a empty, reserved next label available, so expect to
        # read on an invalid error once.
        except IndexError:
            continue


        statement = ("SELECT taxonomy FROM {}_term_taxonomy WHERE "
                     "term_id = {}".format(prefix, label.get("term_taxonomy_id")))
        cursor.execute(statement)
        result = cursor.fetchall()
        label_type = result[0].get("taxonomy")

        if not labels.get(label_type):
            labels.update({label_type: [label_name]})
        else:
            labels.get(label_type).append(label_name)

    return labels

def build_export(entry, options, authors=None, tags=None, categories=None):
    """Construct the export text which is written to the file."""

    export = "Title: {}\n".format(entry["post_title"])
    export = export + "Date: {}\n".format(entry["post_date"])

    if tags:
        tags_string = ""
        for tag in tags:
            tags_string = tags_string + tag + ","
        export = export + "Tags: {}\n".format(tags_string)

    if categories:
        category_string = ""
        for category in categories:
            category_string = category_string + category + ","
        export = export + "Categories: {}\n".format(category_string)

    if authors:
        export = export + "Author: {}\n".format(authors[entry["post_author"]])

    if options.include_modified_date:
        export = export + "Last Modified: {}\n".format(entry["post_modified"])
    if options.include_published_url:
        export = export + "Permalink: {}\n".format(entry["guid"])


    # special casing for historical posts (e.g. imported from tumblr)
    if entry["post_content_filtered"] == "":
        export = export + "\n{}\n".format(entry["post_content"])
    else:
        export = export + "\n{}\n".format(entry["post_content_filtered"])

    return export

def get_authors(connection, prefix):
    """Get a dictionary of authors from the database."""

    authors = {}

    statement = "SELECT * FROM {}_users".format(prefix)
    cursor = connection.cursor(mdb.cursors.DictCursor)

    cursor.execute(statement)
    results = cursor.fetchall()

    for user in results:
        authors.update({int(user["ID"]): user["display_name"]})

    return authors


def get_content(connection, content_type, prefix):
    """Get the posts/pages from the database."""

    if content_type == "pages":
        content_statement = ("SELECT * FROM {}_posts WHERE post_type ="
            " 'page' AND post_status NOT LIKE 'auto-draft'".format(prefix))

    elif content_type == "posts":
        content_statement = ("SELECT * FROM {}_posts WHERE post_type ="
            " 'post' AND post_status NOT LIKE 'auto-draft'".format(prefix))

    else:
        raise TypeError("{} is not a recognized type of content.".format(
            content_type))

    cursor = connection.cursor(mdb.cursors.DictCursor)
    cursor.execute(content_statement)

    content = cursor.fetchall()

    return content


def parse_arguments():
    """Parse given command line arguments."""

    text_server = "MySQL server you want to connect to"
    text_user = ("Username used for authentication with the MySQL"
                 "instance (default:root)")
    text_database = "MySQL database you want to export data from"
    text_prefix = "Prefix of your Wordpress table (default:wp)"
    text_modified = "Include last modified date in the metadata block."
    text_URL = "Include the published permalink in the metadata block."
    text_tags = "Include tags for posts and pages."
    text_categories = "Include categories for posts and pages."
    text_author = "Include post or page author."

    parser = argparse.ArgumentParser()

    parser.add_argument("server", help=text_server,)
    parser.add_argument("database", help=text_database,)

    parser.add_argument("-u", "--user", help=text_user, default="root")
    parser.add_argument("-p", "--prefix", help=text_prefix, default="wp")

    parser.add_argument("--include-published-url", help=text_URL,
        action='store_true')
    parser.add_argument("--include-modified-date", help=text_modified,
        action='store_true')
    parser.add_argument("--include-categories", help=text_categories,
        action='store_true')
    parser.add_argument("--include-tags", help=text_tags,
        action='store_true')
    parser.add_argument("--include-author", help=text_author,
        action='store_true')

    arguments = parser.parse_args()

    return arguments

def ask_password(options):
    """Get the password from stdin."""

    password_text = "Password for {} on {}: ".format(options.user,
        options.server)

    password = getpass.getpass(password_text)

    return password

def connect(options):
    """Open a connection to the database."""

    password = ask_password(options)
    connection = mdb.connect(options.server, options.user, password,
        options.database)

    return connection

if __name__ == "__main__":
    main()
