from sys import stdin, stdout
from re import match
from select import poll, POLLIN

class ANSI:
    """
    Basic cursor and color control for ANSI terminals.

    References:
        https://en.wikipedia.org/wiki/ANSI_escape_code
        https://ispltd.org/mini_howto/ansi_terminal_codes
    """

    # Basic 3-bit colors
    COLOR_BLACK = 0
    COLOR_RED = 1
    COLOR_GREEN = 2
    COLOR_YELLOW = 3
    COLOR_BLUE = 4
    COLOR_MAGENTA = 5
    COLOR_CYAN = 6
    COLOR_WHITE = 7

    # Text styles
    A_NORMAL = 0
    A_BOLD = 1
    A_DIM = 2
    A_UNDERLINE = 4
    A_INVERSE = 7

    # Special keypad keys
    KEY_DOWN = 0x102
    KEY_UP = 0x103
    KEY_LEFT = 0x104
    KEY_RIGHT = 0x105
    KEY_HOME = 0x106
    KEY_BACKSPACE = 0x107
    KEY_F0 = 0x108
    KEY_F1 = 0x109
    KEY_F2 = 0x10A
    KEY_F3 = 0x10B
    KEY_F4 = 0x10C
    KEY_DC = 0x14A  # Delete
    KEY_IC = 0x14B  # Insert
    KEY_NPAGE = 0x152  # Next page (PgDn)
    KEY_PPAGE = 0x153  # Prev page (PgUp)
    KEY_END = 0x168

    keypad_sequence = {
        'A': KEY_UP,
        'B': KEY_DOWN,
        'C': KEY_RIGHT,
        'D': KEY_LEFT,
        'F': KEY_END,
        'H': KEY_HOME,
        '1~': KEY_HOME,
        '2~': KEY_IC,
        '3~': KEY_DC,
        '4~': KEY_END,
        '5~': KEY_PPAGE,
        '6~': KEY_NPAGE,
        '11~': KEY_F1,
        '12~': KEY_F2,
        '13~': KEY_F3,
        '14~': KEY_F4,
    }

    # Escape sequences
    ESC = '\x1B'
    RESET = 'c'

    # Control sequences
    CSI = ESC + '['
    CUP = 'H'   # move cursor to Line;Col
    DSR = '6n'  # query cursor position
    ED2 = '2J'  # erase screen
    ED3 = '3J'  # erase screen and scrollback
    EL0 = '0K'  # erase line to end
    EL1 = '1K'  # erase line to beginning
    EL2 = '2K'  # erase entire line

    def __init__(self):
        self.reset()
        self.cursor = (1,1)
        self.echo = True
        self.use_keypad = True

    def clear(self, clear_scrollback=False):
        """
        Remove all text from the display. Does not move cursor.
        """
        if (clear_scrollback == True):
            stdout.write(ANSI.CSI + ANSI.ED3)
            stdout.write(ANSI.CSI + ANSI.ED2)
        else:
            stdout.write(ANSI.CSI + ANSI.ED2)

    def clear_line(self):
        """
        Erase the entire line at the current cursor position.
        """
        stdout.write(ANSI.CSI + ANSI.EL2)

    def set_color(self, color_pair=(COLOR_WHITE, COLOR_BLACK)):
        """
        Set the foreground and background colors. Accepts 0..7 (3-bit) colors as a tuple.
        Refer to the predefined color constants for possible values.
        """
        fg_color, bg_color = color_pair
        fg_code = fg_color + 30
        bg_code = bg_color + 40
        stdout.write(ANSI.CSI + str(fg_code) + ';' + str(bg_code) + 'm')

    color = property(None, set_color)

    def get_cursor(self):
        """
        Return cursor (line, col) coordinates as a tuple.
        """
        stdout.write(ANSI.CSI + ANSI.DSR)
        reply = ''  # Expecting reply with no newline in the form: 'ESC[{line};{col}R'
        while True:
            ch = stdin.read(1)
            reply += ch
            if (ch == 'R'):
                break

        reply = reply.lstrip('\x1B[')
        reply = reply.rstrip('R')
        if (match('[0-9]+;[0-9]+', reply)):
            line, col = reply.split(';')
        else:
            line, col = ('0', '0')  # Coordinates are 1-based, so (0,0) is impossible.
        
        return int(line), int(col)

    def set_cursor(self, line_col):
        """
        Move cursor to new line, col.
        """
        line, col = line_col
        stdout.write(ANSI.CSI + str(line) + ';' + str(col) + ANSI.CUP)

    cursor = property(get_cursor, set_cursor)

    def reset(self):
        """
        Reset terminal and probe for terminal dimensions. Clears screen.
        """
        stdout.write(ANSI.ESC + 'c')
        self.cursor = (999,999)              # Move cursor far past screen limits.
        self.lines, self.cols = self.cursor  # It will stop at (last line, last col).
        self.cursor = (1,1)

    def set_style(self, style=A_NORMAL):
        stdout.write(ANSI.CSI + str(style) + 'm')

    style = property(None, set_style)

    def getch(self):
        """
        Wait for a keypress and return its value as an integer. Optionally
        process keypad and function keys.
        """
        ch = None
        poll_obj = poll()
        poll_obj.register(stdin, POLLIN)
        while (True):
            keypress = stdin.read(1) if poll_obj.poll(0) else None
            if keypress != None:
                if self.echo == True:
                    stdout.write(keypress)
                ch = ord(keypress)
                if ch != 0x1B or self.use_keypad == False:  # Not an ESC sequence
                    break
                elif stdin.read(1) == '[':  # ESC[ is Control Sequence Introducer
                    sequence = ''
                    while True:
                        s = stdin.read(1)
                        sequence += s
                        if ord(s) > 0x3F and ord(s) < 0x7F:
                            break
                    ch = ANSI.keypad_sequence.get(sequence)
                    break
        return ch
