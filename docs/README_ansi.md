# ansi.py
The ANSI class gives you a straightforward way to control your ANSI
(or VT100) compliant terminal emulator. It's a little like ncurses in
concept, but it's not a direct mapping of C functions to Python.
Instead, ANSI takes advantage of class objects and lets you interact
with your terminal emulator by assigning values to properties.

Here's an example:
```
from ansi import ANSI
terminal = ANSI()
terminal.color = (ANSI.COLOR_GREEN, ANSI.COLOR_BLACK)
print('Press any key to continue')
keypress = terminal.getch()
terminal.style = ANSI.BOLD
print('You pressed the {:s} key!'.format(keypress))
```

You can also move the cursor around, clear the screen, clear a single line,
set the area of the screen that scrolls up/down, etc.

For more examples, see the as of yet incomplete Femto editor
[femto.py](../femto.py).