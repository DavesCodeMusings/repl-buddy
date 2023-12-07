from sys import stdin, stdout
from re import match
from select import poll, POLLIN

"""
Basic cursor and color control for ANSI terminals.

References:
    https://en.wikipedia.org/wiki/ANSI_escape_code
    https://ispltd.org/mini_howto/ansi_terminal_codes
    https://www2.ccs.neu.edu/research/gpc/VonaUtils/vona/terminal/vtansi.htm
"""


class Cursor:
    def __init__(self):
        pass

    def __str__(self):
        line, col = self.get_coord()
        return "Ln: {:d}, Col: {:d}".format(line, col)

    def get_coord(self):
        """
        Return cursor (line, col) coordinates as a tuple.
        """
        stdout.write(ANSI.CSI + "6n")
        reply = ""  # Expecting reply with no newline in the form: 'ESC[{line};{col}R'
        while True:
            ch = stdin.read(1)
            reply += ch
            if ch == "R":
                break

        reply = reply.lstrip(ANSI.CSI)
        if match("[0-9]+;[0-9]+R", reply):
            reply = reply.rstrip("R")
            line, col = reply.split(";")
        else:
            line, col = (0, 0)  # Coordinates are 1-based, so (0,0) is impossible.

        return int(line), int(col)

    def set_coord(self, line_col):
        """
        Move cursor to new line, col coordinates.
        """
        line, col = line_col
        stdout.write(ANSI.CSI + "{:d};{:d}H".format(line, col))

    coord = property(get_coord, set_coord)

    def show(self):
        """
        Make the cursor visible on the terminal screen.
        """
        stdout.write(ANSI.CSI + "?25h")

    def hide(self):
        """
        Remove the cursor from the screen.
        """
        stdout.write(ANSI.CSI + "?25l")

    def save(self):
        """
        Ask terminal to save the cursor position, text attributes, and colors.
        """
        stdout.write(ANSI.ESC + "7")

    def restore(self):
        """
        Restore the previously saved position, attributes, and colors.
        """
        stdout.write(ANSI.ESC + "8")


class ANSI:
    # Escape sequences
    ESC = "\x1B"
    CSI = ESC + "["  # Control Sequence Introducer

    # Text attibutes
    NORMAL = 0  # cancel all attributes and colors
    BOLD = 1
    DIM = 2
    UNDERLINE = 4
    INVERSE = 7
    NOT_BOLD = 22
    NOT_DIM = 22
    NOT_UNDERLINE = 24
    NOT_INVERSE = 27

    # Basic 3-bit colors
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

    # Non-alpha-numeric keys
    KEY_ENTER = 0x0A
    KEY_ESC = 0x1B
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
        "A": KEY_UP,
        "B": KEY_DOWN,
        "C": KEY_RIGHT,
        "D": KEY_LEFT,
        "F": KEY_END,
        "H": KEY_HOME,
        "1~": KEY_HOME,
        "2~": KEY_IC,
        "3~": KEY_DC,
        "4~": KEY_END,
        "5~": KEY_PPAGE,
        "6~": KEY_NPAGE,
        "11~": KEY_F1,
        "12~": KEY_F2,
        "13~": KEY_F3,
        "14~": KEY_F4,
    }

    def __init__(self):
        self.cursor = Cursor()
        self.echo = True
        self.use_keypad = True
        self.reset()

    ### Entire Screen ###

    def reset(self):
        """
        Reset terminal and probe for terminal dimensions. Clears screen.
        """
        stdout.write(ANSI.ESC + "c")
        self.cursor.coord = (999, 999)  # It will stop at (last line, last col).
        self.lines, self.cols = self.cursor.coord
        self.cursor.coord = (1, 1)

    def clear(self, before_cursor=True, after_cursor=True, clear_scrollback=False):
        """
        Erase the screen, either the entire screen (default) or just the
        lines before/after the cursor line.
        """
        if clear_scrollback is True:
            stdout.write(ANSI.CSI + "3J")

        if after_cursor and not before_cursor:
            control_sequence = "J"
        elif before_cursor and not after_cursor:
            control_sequence = "1J"
        elif after_cursor and before_cursor:
            control_sequence = "2J"

        stdout.write(ANSI.CSI + control_sequence)

    ### Scroll Region ###

    def set_scroll_region(self, row_range):
        """
        Limit range of rows (inclusive) affected when scrolling up/down.
        """
        if len(row_range) != 2:
            return False
        top, bottom = row_range
        stdout.write(ANSI.CSI + "{:d};{:d}r".format(top, bottom))

    def clear_scroll_region(self):
        stdout.write(ANSI.CSI + "r")

    scroll_region = property(None, set_scroll_region, clear_scroll_region)

    def scroll_up(self):
        stdout.write(ANSI.CSI + "S")

    def scroll_down(self):
        stdout.write(ANSI.CSI + "T")

    ### Individual Lines ###

    def clear_line(self, before_cursor=True, after_cursor=True):
        """
        Erase the line where the cursor is currently located, either the
        entire line (default) or before/after the cursor column.
        """
        if after_cursor and not before_cursor:
            control_sequence = "K"
        elif before_cursor and not after_cursor:
            control_sequence = "1K"
        elif after_cursor and before_cursor:
            control_sequence = "2K"

        stdout.write(ANSI.CSI + control_sequence)

    def next_line(self):
        """
        Go to the next line and position the cursor at the beginning.
        """
        stdout.write(ANSI.CSI + "E")

    ### Individual Characters ###

    def set_attributes(self, attributes_triplet=(NORMAL, WHITE, BLACK)):
        """
        Define text style (bold, inverse, etc.) and colors. Refer to
        predefined attribute and color constants for possible values.
        """
        if len(attributes_triplet != 3):
            return False
        style, fg_color, bg_color = attributes_triplet
        control_sequence = "{:d};".format(style) if style else ""
        control_sequence += "{:d};".format(fg_color + 30) if fg_color else ""
        control_sequence += "{:d};".format(bg_color + 40) if bg_color else ""
        control_sequence = control_sequence.rstrip(";")
        control_sequence += "m"
        stdout.write(ANSI.CSI + control_sequence)

    def clear_attributes(self):
        """
        Reset text attributes and colors back to default.
        """
        stdout.write(ANSI.CSI + "m")

    attributes = property(None, set_attributes, clear_attributes)

    def set_color(self, color_pair=(WHITE, BLACK)):
        """
        Set the foreground and background colors. Refer to predefined
        color constants for possible values.
        """
        if len(color_pair) != 2:
            return False
        fg_color, bg_color = color_pair
        stdout.write(ANSI.CSI + "{:d};{:d}m".format(fg_color + 30, bg_color + 40))

    def clear_color(self):
        """
        Reset colors to default without affecting attributes (bold, etc.)
        """
        stdout.write(ANSI.CSI + "39;49m")  # 39;49 represent default.

    color = property(None, set_color, clear_color)

    def set_style(self, style_attr):
        stdout.write(ANSI.CSI + "{:d}m".format(style_attr))

    def clear_style(self):
        stdout.write(ANSI.CSI + ANSI.NORMAL + "m")

    style = property(None, set_style, clear_style)

    ### Keyboard Input ###

    def getch(self):
        """
        Wait for a keypress and return its value as an integer. Optionally
        process keypad and function keys.
        """
        ch = None
        poll_obj = poll()
        poll_obj.register(stdin, POLLIN)
        while True:
            keypress = stdin.read(1) if poll_obj.poll(0) else None
            if keypress is not None:
                if self.echo is True:
                    stdout.write(keypress)
                ch = ord(keypress)
                if (
                    ch != ANSI.KEY_ESC or self.use_keypad is False
                ):  # Not an ESC sequence
                    break
                elif stdin.read(1) == "[":  # ESC[ is Control Sequence Introducer
                    sequence = ""
                    while True:
                        s = stdin.read(1)
                        sequence += s
                        if ord(s) > 0x3F and ord(s) < 0x7F:
                            break
                    ch = ANSI.keypad_sequence.get(sequence)
                    break
        return ch

    ch = property(getch)
