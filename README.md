# REPL Buddy
Collection of Python functions to make REPL more like *nix shell

## What is it?
REPL Buddy lets you use familiar shell command names to do things at the REPL kind of like you would at a shell prompt.

For an explanation, let's look at some examples.

### Want to list files?

#### REPL
```
>>> os.listdir()
['boot.py', 'hello.py', 'lib', 'test1.txt', 'test2.txt', 'tmp']
```

_Uh, sure, I guess._

#### REPL Buddy
```
>>> ls()
total 6
type  size  mtime         name
-      292  NOV  6 14:31  boot.py
-        0  NOV  6 19:59  hello.py
d        2  JAN  1 00:00  lib
-        0  NOV  6 19:58  test1.txt
-        0  NOV  6 19:58  test2.txt
d        2  JAN  1 00:00  tmp
```

_Mmm, so smooth and satisfying!_

### Want to search a file to see if it contains a regex string?

#### REPL
```
import os
import re
#$@%&^!
requests.get('stackoverflow.com')
```

_Good luck with that!_

#### REPL Buddy
```
>>> grep('Hello', 'hello.py')
print('Hello Cleveland!')
```

_Che bella!_

## How do I use it?
It's easy. Just grab `repl_buddy.py` from this repository and save it to `/lib/repl_buddy.py` on your MicroPython device. Then import the functions like this:

```
from repl_buddy import *
```

The following functions will be available to you:

* `cat(FILE1, [FILE2], ...)` display contents of one or more files
* `cd([DIRNAME])` change directory to DIRNAME or / if no parameter given
* `date([SECONDS])` display the current date and time or the date given by SECONDS from the Python epoch 
* `grep(PATTERN, FILENAME)` search for PATTERN in FILENAME and print matching lines
* `ls(FILENAME | DIRNAME)` list the properties of FILENAME or the properties of all files in DIRNAME
* `mkdir(DIRNAME)` create the directory given by DIRNAME
* `mv(SOURCE, DEST)` rename SOURCE to DEST or if DEST is a directory, move SOURCE there
* `pwd()` show the present working directory path
* `rm(FILENAME)` delete FILENAME
* `rmdir(DIRNAME)` delete DIRNAME, but only if it's empty
* `touch(FILENAME)` create a new, empty file or change the modification time stamp on an existing file

REPL Buddy is not a shell, so you'll still have to supply parameters as quoted strings, but it does make things a little more convenient when managing your flash file system.

Most functions should be pretty self-explanitory from their names and descriptions above. Some, llike `cd()` and `ls()` can be called with or without parameters. Those that require parameters will give a brief usage statement if you don't supply what they need.

All of REPL Buddy's functions are severely limited when compared to their *nix shell counterparts. For example, `rm()` has no recursive option, `grep() can only search text files, etc. There's also no way to pipe commands together or redirect output.

Still, it's better than nothing. If you like the functionality, add the line `from repl_buddy import *` to your boot.py.

## I tried it and I found a bug. What now?
Create an issue in GitHub and I'll see if I can fix it. Though please be patient as I am a developer team of one.

## A note about time...
Functions like `ls()` and `touch()` depend on accurate system time for the file modification timestamp. The `date()` function is another obvious one. If you dont set the clock when your microcontroller boots, it's going to think the date-time is Jan 1, 2000 at midnight.

You can remedy this by setting the time in boot.py:
```
from ntptime import settime
settime()
```
