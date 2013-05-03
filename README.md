# thinout.py

A Python program frame to selectively remove old backups,
or similar files.

## Motivation

If you for example make daily backups of a database you collect a
lot of backup files over time. Older files can be deleted after some
time to save disk space.

But usually you don't want to just delete all files older than X days,
a better strategy is often to first delete maybe just every second backup
file, to keep a longer history.

It is preferable to keep a few older backups around, this gives you
something to fall back on if you need to restore something deleted a
while ago or if the newer backups turn out to be corrupted in some way.

The question which and how many older backups to keep or delete can get
more complicated if backups are only taken irregulary or backups might
fail to be created. In such a situation a simple rule like "After a week,
just keep the backup from Sunday" can easily get all backups deleted if
there was no backup on Sunday.

## Usage

### Example

A sample program would look like this:

    import thinout

    intervalls = [
          (7, 7),
          (30, 5)
       ]
    
    thinout.run('/var/local/backup/homedir-*.tgz', intervalls)

The most interesting part is the `intervalls` definition. It defines a how
many files in which interval should be kept: In the last 7 days, we want
to keep 7 backups. In the 30 days before that, we want do keep just 5
files.

`thinout.run()` then analyzes which files would be best removed to achieve
the sepecified retention rates.

To actually delete the files, you have to specify the `-d` flag, otherwise
it will only be reported which files would be removed.

### Options

**TODO**

### Advanced usage

**TODO**

