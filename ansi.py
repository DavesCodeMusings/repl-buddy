from sys import stdin, stdout
from re import match

class ANSI:
    """
    Basic cursor and color control for ANSI terminals.

    References:
        https://en.wikipedia.org/wiki/ANSI_escape_code
        https://ispltd.org/mini_howto/ansi_terminal_codes
    """

    # Basic 3-bit colors
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

    # Text styles
    NORMAL = 0
    BOLD = 1
    DIM = 2
    UNDERLINE = 4
    INVERSE = 7

    # Escape sequences
    ESC = b'\x1B'
    RESET = 'c'

    # Control sequences
    CSI = '\x1B['
    CUP = 'H'
    DSR = '6n'
    ED2 = '2J'

    def __init__(self):
        """
        Reset terminal.
        """
        self.reset()

    def clear(self):
        """
        Remove all text from the display. Move cursor to (1,1)
        """
        stdout.write(ANSI.CSI + ANSI.ED2)
        self.home()

    def set_color(self, scheme=(WHITE, BLACK)):
        """
        Set the foreground and background colors. Accepts 0..7 (3-bit) colors as a tuple.
        Refer to the predefined color constants for possible values.
        """
        fg_color, bg_color = scheme
        fg_code = fg_color + 30
        bg_code = bg_color + 40
        stdout.write(ANSI.CSI + str(fg_code) + ';' + str(bg_code) + 'm')

    color = property(None, set_color)

    def get_cursor(self):
        """
        Return cursor (row, col) coordinates as a tuple.
        """
        stdout.write(ANSI.CSI + ANSI.DSR)
        reply = ''  # Expecting reply with no newline in the form: 'ESC[{row};{col}R'
        while True:
            ch = stdin.read(1)
            reply += ch
            if (ch == 'R'):
                break

        reply = reply.lstrip('\x1B[')
        reply = reply.rstrip('R')
        if (match('[0-9]+;[0-9]+', reply)):
            row, col = reply.split(';')
        else:
            row, col = ('0', '0')  # Coordinates are 1-based, so (0,0) is impossible.
        
        return int(row), int(col)

    def set_cursor(self, coord):
        """
        Move cursor to (row, col) given by the coord tuple.
        """
        row, col = coord
        stdout.write(ANSI.CSI + str(row) + ';' + str(col) + ANSI.CUP)

    cursor = property(get_cursor, set_cursor)

    def home(self):
        """
        Move the cursor to coordinates (1,1). Does not clear the screen.
        """
        stdout.write(ANSI.CSI + ANSI.CUP)

    def reset(self):
        """
        Clear screen. Probe for terminal dimensions. Move cursor to (1,1).
        """
        stdout.write(ANSI.ESC + 'c')
        self.cursor = (999,999)                   # Move cursor far past screen limits.
        self.rows, self.cols = self.get_cursor()  # It will stop at (last row, last col).
        self.cursor = (1,1)


    def set_style(self, style=NORMAL):
        stdout.write(ANSI.CSI + str(style) + 'm')

    style = property(None, set_style)
