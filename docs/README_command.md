# command.py
command.py offers a dozen or so functions modeled after popular *nix
shell commands.

Here's an example:
```
>>> from command import *

>>> ls()
total 6
type  size  mtime         name
-      292  NOV  6 14:31  boot.py
-       60  Nov  6 14:38  config.py
-        0  NOV  6 19:59  hello.py
d        2  JAN  1 00:00  lib
-        0  NOV  6 19:58  test1.txt
-        0  NOV  6 19:58  test2.txt
d        2  JAN  1 00:00  tmp

>>> grep('NAME', 'config.py')
AP_NAME='myssid'
```

## Available commands
Most of the functions take parameters similar to their command counterparts.
See the list below for specifics.

* `cat(FILE1, [FILE2], ...)`
    display contents of one or more files
* `cd([DIRNAME])`
    change directory to DIRNAME or / if no parameter given
* `clear()`
    move cursor to top left corner and clear the screen (ANSI
    terminals only)
* `date([SECONDS])`
    display the current date and time or the date given by SECONDS
    from the Python epoch
* `df([PATH])`
    show file system usage statistics for PATH or the current working
    directory if PATH is not specified
* `grep(PATTERN, FILENAME)`
    search for PATTERN in FILENAME and print matching lines
* `ls(FILENAME | DIRNAME)`
    list the properties of FILENAME or the properties of all files
    in DIRNAME
* `mkdir(DIRNAME)`
    create the directory given by DIRNAME
* `mv(SOURCE, DEST)`
    rename SOURCE to DEST or if DEST is a directory, move SOURCE there
* `pwd()`
    show the present working directory path
* `recv([FILENAME], [EOF])`
    receive text from STDIN and write to FILENAME until EOF is entered
    on a line by itself
* `rm(FILENAME)`
    delete FILENAME
* `rmdir(DIRNAME)`
    delete DIRNAME, but only if it's empty
* `run(FILENAME)`
    execute the Python script given by FILENAME 
* `touch(FILENAME)`
    create a new, empty file or change the modification time stamp on
    an existing file

## Limitations
Since you're at a REPL prompt and not a shell prompt, you need to put
quotes around your parameters and use commas and parentheses. It's also
not possible to pipe one function to another.

### Won't work
```
cat('test1.txt') | grep('string')
```

### Does work
```
grep('string', 'test.txt')
```

## Date and time
You may notice strange dates on your files and Jan 1, 2000  being
reported by the `date()` function. This is due to the microcontroller
not having its clock set properly.

You can fix it with a couple lines in `boot.py`
```
from ntptime import settime
settime()
```
