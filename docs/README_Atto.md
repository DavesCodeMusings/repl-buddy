# The Atto Editor
Atto is a line editor for MicroPython that mimics a subset of the
functionality available in the `ed` editor. Like `ed`, Atto is a pain
in the tuchas to use, but it can be handy for making minor changes to
files when nothing else is available.

Here's an example of using Atto to make a simple config change.
```
>>> from atto import *
>>> atto('config.py')
3 lines read from config.py
*%n
1 AP_NAME='myssid'
2 AP_PASS='oops_wrong_password'
3 AP_TIMEOUT = 30
*2c
Enter a single . to exit input mode.
>AP_PASS='CorrectPassword'
>.
*%p
AP_NAME='myssid'
AP_PASS='CorrectPassword'
AP_TIMEOUT = 30
*w
3 lines written to config.py
*q
```

Let's break that down...

## Loading the module
```
>>> from atto import *
```

Nothing special here. After this, the `atto()` function is available
for you to use. You can edit any text file by including its path as
a parameter to atto().

## Editing a file
```
>>> atto('config.py')
3 lines read from config.py
```

Atto has been started and has successfully loaded config.py into its
buffer. You are then greeted with a rather minimalist `*` command
prompt. Atto commands closely follow `ed` commands, but lack any
regular expression features beyond searching the buffer for a matching
line.

## Listing numbered lines
```
*%n
1 AP_NAME='myssid'
2 AP_PASS='oops_wrong_password'
3 AP_TIMEOUT = 30
```

The `n` command is used to show lines with line numbers. The % is a
character that denotes _all lines_ from 1 to the end. This makes it
easier to identify the line that needs changing.

## Changing a line
```
*2c
```

The `c` command means change. The number in front of it specifies the
line number to change. In this case, it's line 2.

## Entering the new line
```
Enter a single . to exit input mode.
>AP_PASS='CorrectPassword'
>.
```

The prompt will change from `*` to `>` indicating you are now in insert
mode. Line 2 has been deleted and you'll need to re-enter it in its
entirety. When you're done, a single `.` after the input prompt will
return you to command mode.

## Verifying the change
```
*%p
AP_NAME='myssid'
AP_PASS='CorrectPassword'
AP_TIMEOUT = 30
```

The `p` command will print lines. It's like the `n` command, but without
the numbering. You can see your change has been made in the buffer.

## Save the change and exit
```
*w
3 lines written to config.py
*q
```
The `w` command will write the contents of the buffer to back to the file.
The `q` command will exit the program.

## Alternate ways to find the line you're looking for
```
*/PASS/n
2 AP_PASS='oops_wrong_password'
```

It was easy to identify the parameter that needed changing in the example.
After all, there were only three lines. If you didn't know the line number
but knew it had the word `PASS` in it, you could use regex matching.

The pair of forward slashes marks the regex string. The `n` command includes
the line number with the result. If you were confident only one line would
have the string 'PASS', you could use `/PASS/c` to go directly to changing
the line without listing it first.

## More info
Since Atto closely follows `ed`, you can use just about any `ed` tutorial
you can find to figure out how to do what you need to do. However, keep in
mind Atto does not offer any RegEx features beyond simple addressing.

Atto is also slightly more friendly than `ed` and includes a help feature.
You can get a brief reminder of available commands by entering `h` at the
`*` prompt.

```
*h
Usage: {addr}cmd

Line Addressing
------------------------------
{n}         single line
{n1},{n2}   range of lines
.           current line
$           last line
%           all lines 1,$
/regexp     next matching line

Command Summary
---------------------------------------
{n}a        Append new line(s) after
{n1},{n2}c  Change (replace) line(s)
{n1},{n2}d  Delete line(s)
e [path]    Edit new file
f [path]    View/change filename
{n}i        Insert new line(s) before
{n1},{n2}n  Print with numbered lines
{n1},{n2}p  Print
q           Quit
w [path]    Write (save) buffer to file
```

## What's with the name?
_atto_ (combining form)
    _a metric system unit prefix denoting 10 to the -18 power_

Pico and Nano are names of editors available on Linux systems. Atto is
considerably less powerful and feature rich than either of these. Hence
the name of a prefix that denotes something much smaller than a nano or
pico-sized unit.
