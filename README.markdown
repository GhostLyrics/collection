# GhostLyrics's Collection

A collection of scripts I've written either for myself or during work. These scripts are intended to be runable as single files, unless configuration is necessary.

## archive-home

Archive and remove a user's home directory.

Home directories are moved to trash instead of deleted immediately.
If SSH keys are archived the user is notified.
Allows to perform a `--dry-run`.

**Depends on trash-cli/trash.**

- Linux: https://github.com/andreafrancia/trash-cli  
- OS X: http://hasseg.org/trash/

```none
usage: archive-home.py [-h] [-d] [-v] user

positional arguments:
  user           the user whose home directory should be archived

optional arguments:
  -h, --help     show this help message and exit
  -d, --dry-run  run in simulated mode and only print actions
  -v, --verbose  display messages about program flow
```

## archive-mailman

Archive and remove a mailman mailing list.

Lists are deleted with the mailman provided `rmlist` interface.
Allows to perform a --dry-run.

**Depends on mailman provided `rmlist`.**

```none
usage: archive-mailman.py [-h] [-d] [-v] [-p PATH] listname

positional arguments:
  listname              the mailman mailing list to archive and remove

optional arguments:
  -h, --help            show this help message and exit
  -d, --dry-run         run in simulated mode and only print actions
  -v, --verbose         display messages about program flow
  -p PATH, --archives-path PATH
                        the path to the mailman folder
```

## boot-into-windows

Automatically find a Windows based GRUB boot entry and reboot into it right now.

```none
usage: boot-into-windows.py [-h] [-v]

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  print detailed information about program flow
```

## check-raid-status

Check RAID controller for health information, write to syslog. Works with controllers of type MegaRAID and 3ware. Shows progress while rebuilding.  Allows checking of multiple controllers.

**Depends on the vendor specific binaries for MegaRAID** (`storcli64`) **and 3ware** (`tw_cli`) **being installed and in the PATH.**

```none
usage: check-raid-status.py [-h] type controller [controller ...]

positional arguments:
  type        type of RAID controller (supported: MegaRAID or 3ware)
  controller  number of RAID controller

optional arguments:
  -h, --help  show this help message and exit
  --cron-mode complain about drive issues to stdout
```

## download-slack-files

Download all files linked in a Slack export archive.
All uploaded files are downloaded into their respective channel folders.
Optionally, Slack IDs can be used instead of file names.

```none
usage: download-slack-files.py [-h] [--remote-name] folder

positional arguments:
  folder         the unzipped Slack export directory

optional arguments:
  -h, --help     show this help message and exit
  --remote-name  keep Slack file IDs instead of using the file names
```

## extract-content-from-wordpress-mysql

Extract the content from a MySQL based WordPress installation and write to individual Markdown files. *Auto-drafts will be suppressed. Non standard table prefixes are supported.*

**Depends on MySQLdb module.**

```none
usage: extract-content-from-wordpress-mysql.py [-h] [-u USER] [-p PREFIX]
                                               [--include-published-url]
                                               [--include-modified-date]
                                               [--include-categories]
                                               [--include-tags]
                                               [--include-author]
                                               server database

positional arguments:
  server                MySQL server you want to connect to
  database              MySQL database you want to export data from

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Username used for authentication with the
                        MySQLinstance (default:root)
  -p PREFIX, --prefix PREFIX
                        Prefix of your Wordpress table (default:wp)
  --include-published-url
                        Include the published permalink in the metadata block.
  --include-modified-date
                        Include last modified date in the metadata block.
  --include-categories  Include categories for posts and pages.
  --include-tags        Include tags for posts and pages.
  --include-author      Include post or page author.
```

## unsubscribe-me

Send unsubscribe notices from specified addresses to specified targets.

**You need to control your own local mailserver.**

```none
usage: unsubscribe-me.py [-h] [--dry-run] -s SENDER -r RECIPIENT

optional arguments:
  -h, --help            show this help message and exit
  --dry-run             Perform a dry run. Do not send out real mail.
  -s SENDER, --sender SENDER
                        The e-mail address you want to send from.
  -r RECIPIENT, --recipient RECIPIENT
                        The e-mail address you want to send to.
```
