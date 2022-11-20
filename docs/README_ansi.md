# ansi.py
The ANSI class provides a straightforward way to control your ANSI
(VT100) compliant terminal emulator. It's a little like ncurses in
concept, but it's not a direct mapping of ncurses C functions to Python.
Instead, ANSI takes advantage of class objects and lets you interact
with your terminal emulator by assigning values to properties.

Here's a simple example of changing colors and getting input:
```
from ansi import ANSI
terminal = ANSI()
terminal.color = (ANSI.GREEN, ANSI.BLACK)
print('Press any key to continue')
keypress = terminal.getch()
terminal.style = ANSI.BOLD
print('You pressed the {:s} key!'.format(keypress))
```

You can also move the cursor around and print lines in inverse (dark
on light) text.

Here's a more complex example presenting an interactive menu:

```
from ansi import ANSI
terminal = ANSI()
terminal.clear()
terminal.echo = False
terminal.color = (ANSI.YELLOW, ANSI.BLACK)
terminal.cursor.coord = (1,1)

menu_items = ['apricot', 'cherry', 'huckleberry', 'lychee']
selected_item = 0

row, col = terminal.cursor.coord
while True:
    terminal.cursor.save()
    for i in range(0, len(menu_items)):
        terminal.style = ANSI.INVERSE if (i == selected_item) else ANSI.NOT_INVERSE
        print(menu_items[i])
    terminal.cursor.restore()

    terminal.cursor.hide()
    ch = terminal.getch()
    if ch == ANSI.KEY_ENTER:
        break
    elif ch == ANSI.KEY_UP:
        if selected_item > 0:
            selected_item -= 1
    elif ch == ANSI.KEY_DOWN:
        if selected_item < len(menu_items) - 1:
            selected_item += 1
    else:
        print(ch)

terminal.clear()
terminal.cursor.coord = (row, col)
print(menu_items[selected_item])
```

For more examples, see the as of yet incomplete Femto editor
[femto.py](../femto.py).
