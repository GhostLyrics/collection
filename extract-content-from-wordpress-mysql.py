#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xml.dom.minidom import parseString
import MySQLdb as mdb
import array
import sys
import os


class connection:
    def __init__(self):
        with open('config.xml', 'r') as config:
            xml = config.read()
            dom = parseString(xml)
            # read the server
            xmlServer = dom.getElementsByTagName('server')[0].toxml()
            self.server = xmlServer.replace('<server>',
                                            '').replace('</server>', '')
            # read the user
            xmlUser = dom.getElementsByTagName('user')[0].toxml()
            self.user = xmlUser.replace('<user>',
                                        '').replace('</user>', '')

            # read the database name
            xmlDatabase = dom.getElementsByTagName('database')[0].toxml()
            self.database = xmlDatabase.replace('<database>',
                                                '').replace('</database>', '')

            # read the password. Use empty password if no tag exists,
            # handle empty, non-valid XML strings by correcting to empty
            # password.
            try:
                xmlPassword = dom.getElementsByTagName('password')[0].toxml()
                password = xmlPassword.replace('<password>',
                                               '').replace('</password>', '')

                if password == "<password/>":
                    self.password = ""
                    print "WARNING: Empty Strings are not valid XML."
                    print "WARNING: Remove empty tag to use no password."
                else:
                    self.password = password

            except IndexError, e:
                print "No password found: using empty password."
                self.password = ""


def exportDataset(row, path):
    row["post_author"] = id_list.get(row["post_author"])
    # using post_name here, this is the url version that should
    # be safe to use for filenames
    with open(path + "/" + row["post_name"] + ".txt", "w") as file_export:

        export_block = """
Title: %s

%s

METADATA:
Author: %s
Source URL: %s
Originally Published: %s
Last Modified: %s""" % (row["post_title"], row["post_content"],
                        row["post_author"], row["guid"], row["post_date"],
                        row["post_modified"])

        file_export.write(export_block)

con = None
target = connection()


try:
    con = mdb.connect(target.server, target.user,
                      target.password, target.database)

    with con:
        # DictCursor makes results of query accessible in dictionary instead
        # of using tuples
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT * FROM journal_users")
        authors = cur.fetchall()
        id_list = {}
        # fix system created posts having author ID '0'
        for user in authors:
            id_list.update({int(user["ID"]): user["display_name"]})

        # Handling posts of type "post", excluding auto-drafts here
        cur.execute("SELECT * FROM journal_posts WHERE post_type = 'page' AND " +
                    "post_status NOT LIKE 'auto-draft'")

        pages = cur.fetchall()
        for row in pages:
            if os.path.exists("./pages") is False:
                os.mkdir("pages")
            exportDataset(row, "pages")

        # Handling posts of type "page", excluding auto-drafts again
        cur.execute("SELECT * FROM journal_posts WHERE post_type = 'post' AND " +
                    "post_status NOT LIKE 'auto-draft'")

        posts = cur.fetchall()
        for row in posts:
            if os.path.exists("./posts") is False:
                os.mkdir("posts")
            exportDataset(row, "posts")


except mdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)
finally:
    if con:
        con.close()
