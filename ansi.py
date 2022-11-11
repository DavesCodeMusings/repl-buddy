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
    ED3 = '3J'
    EL2 = '2K'

    def __init__(self):
        """
        Reset terminal.
        """
        self.reset()

    def clear(self, clear_scrollback=False):
        """
        Remove all text from the display. Move cursor to (1,1)
        """
        if (clear_scrollback == True):
            stdout.write(ANSI.CSI + ANSI.ED3)
            stdout.write(ANSI.CSI + ANSI.ED2)
        else:
            stdout.write(ANSI.CSI + ANSI.ED2)
        self.home()

    def clear_line(self):
        stdout.write(ANSI.CSI + ANSI.EL2)

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

    def get_key(self, raw=False):
        """
        Wait for a keypress and return its value as a string. When not in raw mode:
          * printable characters are returned unaffected
          * control characters are converted to caret and letter (e.g. CTRL+A becomes ^A)
          * backspace (to the right of +/= key on PC keyboard) is converted to '^H'
          * arrow keys are converted to their ANSI abbreviations
          * Home, End, Insert, Delete, PgUp, PgDn are returned as aforementioned abbreviations
          * Function keys F1 .. F4 are returned as strings 'F1' .. 'F4'
          * Function keys beyond F4 and other special characters are ignored
        """
        key = None
        poll_obj = poll()
        poll_obj.register(stdin, POLLIN)
        while (True):
            ch = stdin.read(1) if poll_obj.poll(0) else None
            if (ch != None):
                if (raw == True):
                    key = ch
                    break
                else:
                    if (ord(ch) >= 32 and ord(ch) < 127):  # printable
                        key = ch
                        break
                    elif (ord(ch) == 27):  # ESC
                        if (stdin.read(1) == '['):  # ESC[ is Control Sequence Introducer
                            sequence = stdin.read(1)
                            if (sequence == 'A'):
                                key = 'CUU'  # up
                                break
                            elif (sequence == 'B'):
                                key = 'CUD'  # down
                                break
                            elif (sequence == 'C'):
                                key = 'CUF'  # forward
                                break
                            elif (sequence == 'D'):
                                key = 'CUB'  # back
                                break
                            elif (sequence == 'F'):
                                key = 'End'
                                break
                            elif (sequence == 'H'):
                                key = 'Home'
                                break
                            elif (ord(sequence) > ord('0') and ord(sequence) < ord('9')):
                                sequence += stdin.read(1)
                                if (sequence.endswith('~') == False):
                                    sequence += stdin.read(1)  # some sequences are 2-digit
                                if (sequence == '1~'):
                                    key = 'Home'
                                    break
                                elif (sequence == '2~'):
                                    key = 'Insert'
                                    break
                                elif (sequence == '3~'):
                                    key = 'Delete'
                                    break
                                elif (sequence == '4~'):
                                    key = 'End'
                                    break
                                elif (sequence == '5~'):
                                    key = 'PgUp'
                                    break
                                elif (sequence == '6~'):
                                    key = 'PgDn'
                                    break
                                elif (sequence == '7~'):  # Yes, this is a repeat
                                    key = 'Home'
                                    break
                                elif (sequence == '8~'):  # Yes, this is a repeat
                                    key = 'End'
                                    break
                                elif (sequence == '11~'):
                                    key ='F1'
                                    break
                                elif (sequence == '12~'):
                                    key ='F2'
                                    break
                                elif (sequence == '13~'):
                                    key ='F3'
                                    break
                                elif (sequence == '14~'):
                                    key ='F4'
                                    break
                                else:
                                    break
                    elif (ord(ch) < 32):  # CTRL keys other than ESC
                        key = '^' + chr(64 + ord(ch))  # CTRL+A becomes ^A
                        break
                    elif (ord(ch) == 127):
                        key = '^H'
                        break
                    else:
                        key = None
                        break
        return key
