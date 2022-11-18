# REPL Buddy
Collection of Python functions to make REPL more like *nix shell

## What is it?
REPL Buddy lets you interact with the MicroPython REPL in ways that mimic
a shell prompt. It provides functions similar to common *nix commands.
There's also a simple line-base editor and a few more features still in
development.

For an explanation, let's look at some examples.

### Want to list files on flash?

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
>>> grep('NAME', 'config.py')
AP_NAME = 'my_ssid'
```

_Che bella!_

### Need to make a change to that config file?
```
from atto import *
atto('config.py')
```

Now you can stare at a `*` prompt and scratch your head just like when
you try to use the `ed` line editor. (But with REPL Buddy's Atto editor
you can at least type `h` to get some help.)

_So retro!_

## How do I use REPL Buddy on my microcontroller?
It's easy. First, you import the command functions like this:
```
from command import *
```

Then, you can use all the functions listed in
[README_command.md](./docs/README_command.md)

Finally, for details on using the Atto editor, there is a brief tutorial
in [README_atto.md](./docs/README_atto.md)

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
