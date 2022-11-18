# REPL Buddy
Collection of Python functions to make REPL more like *nix shell

## What is it?
REPL Buddy lets you interact with the MicroPython REPL in ways that mimic
a shell prompt. It provides functions similar to common *nix commands and
also lets you customize the look your terminal.

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
?#@*&%!!!
requests.get('stackoverflow.com')
```

_Good luck with that!_

#### REPL Buddy
```
>>> grep('Hello', 'hello.py')
print('Hello Cleveland!')
```

_Che bella!_

### Do you like dark mode? Everybody loves dark mode! ###
With standard REPL, color scheme is dictated by your IDE (Integated
Development Environment)

With REPL Buddy's ansi.py, you can use any standard terminal emulator
(like PuTTY) and customize the heck out of it.

```
terminal.color = (ANSI.GREEN, ANSI.BLACK)
terminal.style = ANSI.INVERSE
print('Hello 1980s!')
terminal.style = ANSI.NORMAL
```

_So retro!_

### Want to edit files like it's 1986?
```
from atto import *
atto('filename.txt')
```

Now you can stare at a prompt and scratch your head just like when you
try to use the `ed` line editor. (But you can type ? to get help.)

## How do I use REPL Buddy on my microcontroller?
It's easy. First, you import the command functions like this:
```
from command import *
```

Next, set up the terminal.
```
from ansi import ANSI
terminal = ANSI()
```

Then, the following functions will be available to you:

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
* `select(CHOICE1, [CHOICE2], ...)`
    present a numbered list of choices and return the chosen value
* `touch(FILENAME)`
    create a new, empty file or change the modification time stamp on
    an existing file

## Some important notes
REPL Buddy is not a shell, so you'll still have to supply parameters as
quoted strings, but it does make things a little more convenient when
managing your flash file system.

Most functions should be pretty self-explanitory from their names and
descriptions above. Some, llike `cd()` and `ls()` can be called with or
without parameters. Those that require parameters will give a brief usage
statement if you don't supply what they need.

All of REPL Buddy's functions are severely limited when compared to their
*nix shell counterparts. For example, `rm()` has no recursive option,
`grep()` can only search text files, etc. There's also no way to pipe
commands together or redirect output.

ANSI terminal functions are limited to color, text style, and cursor
position. Additionally, you must connect to the REPL with a terminal that
understands ANSI escape sequences. PuTTY is a good choice. The REPL prompt
built into Thonny is not compatible.

If you like the functionality of REPL Buddy, add the import lines to your
boot.py so it's always available.
```
from command import *
from ansi import ANSI
terminal = ANSI()
```

### Some important notes about `recv()`
`recv()` has no equivalent command in the *nix shell. It takes the place
of using `cat<<EOF >filename.txt` to send STDIN to a file. It offers a
convenient way to upload text files (including MicroPython code) to the
microcontroller by pasting into the terminal.

Using just `recv()` with no parameters writes the pasted input to a file
called recv.txt. Input capture is terminated by entering the string 'EOF'
on a line by itself.

The filename can be changed with a parameter as shown in this example:
`recv('settings.json')`

The end of file marker can be changed as well: `recv(eof_marker='DONE')`

Or you can do both at once: `recv('settings.json', 'DONE')`

#### Caveats concerning recv() and IDE
Using `recv()` from Thonny results in an extra blank line after every line
of text for some reason. This does not happen when using mpremote.

When using mpremote, there is no echo to the terminal from REPL, so you
are flying blind when pasting. If you use Windows Terminal, it will let
you preview what's being pasted. But, it will also try to be helpful and
truncate extra newlines from the end. This makes it hard to put EOF on a
line by itself. Alway press ENTER before and after typing your EOF
sequence into Windows Terminal and you'll be fine.

Using PuTTY to connect to the REPL over a serial port offers the best
experience for uploading files using `recv()`. There's still no echo of
what you paste, but you don't have to worry about PuTTY truncating extra
newlines. Just paste the contents of the clipboard and enter EOF at the
end.

## How do I install or update REPL Buddy?
Use the MicroPython MIP tool, like this:
```
mpremote mip install github:DavesCodeMusings/repl-buddy
```

Or on Windows:
```
py -m mpremote mip install github:DavesCodeMusings/repl-buddy
```

Or download the files directly from
https://github.com/DavesCodeMusings/repl-buddy and save to your device's
/lib directory.

## I tried it and I found a bug. What now?
Create an issue in GitHub and I'll see if I can fix it. Though please be
patient as I am a developer team of one.

## Why is it Y2K all over again?
Functions like `ls()` and `touch()` depend on accurate system time for the
file modification timestamp. The `date()` function is another obvious one.
If you don't set the clock when your microcontroller boots, it's going to
think it's Jan 1, 2000 at midnight.

You can remedy this by setting the time in boot.py, like so:
```
from ntptime import settime
settime()
```
