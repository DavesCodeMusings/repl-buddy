from sys import stdin, stdout
from select import poll, POLLIN
from ansi import ANSI

class Femto:
    CTRL_R = '\x12'
    CTRL_W = '\x17'
    CTRL_X = '\x18'

    def __init__(self, filename=None):
        self._buffer = ''
        self._filename = ''
        if (filename != None):
            self.read(filename)

    def read(self, filename):
        """
        Load file contents into buffer.
        """
        try:
            with open(filename) as f:
                self._buffer = f.readlines()
            self._filename = filename
        except Exception as ex:
            self._filename = ''
            print(ex)

    def write(self, filename=None):
        """
        Save contents of buffer to filename.
        """
        if (filename == None):
            filename = self._filename
        with open(filename, 'w') as f:
            for line in self._buffer:
                f.write(line)

    def purge(self):
        """
        Release the buffer memory and start with a fresh one.
        """
        del self._buffer
        self._buffer = ''

    def dump(self):
        """
        Print buffer lines.
        """
        for line in self._buffer:
            stdout.write(line)

    def list(self):
        """
        Print buffer with line numbers.
        """
        if (len(self._buffer) < 10):
            line_num_field = '{:>1d} '
        elif (len(self._buffer) < 100):
            line_num_field = '{:>2d} '
        elif (len(self._buffer) < 1000):
            line_num_field = '{:>3d} '
        else:
            line_num_field = '{:>4d} '
        current_line_num = 1
        for line in self._buffer:
            stdout.write(line_num_field.format(current_line_num))
            stdout.write(line)
            current_line_num += 1

    def page(self, page_length=20):
        """
        Print buffer, pausing every so many lines.
        """
        current_line_num = 1
        for line in self._buffer:
            if (current_line_num % page_length == 0):
                ch = stdin.read(1)
                if (ch == 'q' or ch == 'Q'):
                    break
            stdout.write(line)
            current_line_num += 1
            
    def _set_status(self, terminal, message):
        """
        Show message on the last line in inverse color scheme.
        """
        cursor_save = terminal.cursor
        terminal.cursor = (terminal.rows, 1)
        terminal.style = ANSI.INVERSE
        message += ' ' * (terminal.cols - len(message))  # pad to fill terminal width
        stdout.write(message)
        terminal.style = ANSI.NORMAL
        terminal.cursor = cursor_save

    def _get_input(self, terminal, prompt):
        """
        Show prompt and capture user reply.
        """
        cursor_save = terminal.cursor
        terminal.cursor = (terminal.rows, 1)
        terminal.style = ANSI.INVERSE
        stdout.write(' ' * (terminal.cols))
        terminal.cursor = (terminal.rows, 1)
        reply = input(prompt)
        terminal.style = ANSI.NORMAL
        terminal.cursor = cursor_save
        return reply

    def visual(self):
        """
        Navigate and edit buffer based on user input.
        """
        terminal = ANSI()

        current_line_num = 1
        for line in self._buffer:
            if (current_line_num > terminal.rows):
                break
            stdout.write(line[:terminal.cols])
            current_line_num += 1

        commands = '[R]ead  [W]rite  e[X]it'
        padding = ' ' * (terminal.cols - len(commands) - len(self._filename))
        self._set_status(terminal, commands + padding + self._filename)

        poll_obj = poll()
        poll_obj.register(stdin, POLLIN)
        while (True):
            ch = stdin.read(1) if poll_obj.poll(1) else None
            if (ch != None):
                if (ch == Femto.CTRL_X):
                    break
                elif (ch == Femto.CTRL_W):
                    self._filename = self._get_input(terminal, 'Filename:')
                    self.write(self._filename)
                elif (ch == Femto.CTRL_R):
                    self._filename = self._get_input(terminal, 'Filename:')
                    self.read(self._filename)
                else:
                    stdout.write(ch)
