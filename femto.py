from sys import stdin, stdout
from select import poll, POLLIN
from ansi import ANSI

class Femto:
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

    def print(self, start=0, stop=None, line_length=None):
        """
        Display a range of buffer lines, possibly truncated to fit.
        """
        if (start > len(self._buffer)):
            start = len(self._buffer) - 1

        if (stop == None or stop > len(self._buffer)):
            stop = len(self._buffer)

        for line_num in range(start, stop):
            if (line_length == None):
                stdout.write(self._buffer[line_num])
            else:
                stdout.write(self._buffer[line_num][:line_length])

    def list(self):
        """
        Print entire buffer with line numbers.
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
        stdout.write(message)
        terminal.cursor = cursor_save

    def _get_input(self, terminal, prompt):
        """
        Show prompt and capture user reply.
        """
        cursor_save = terminal.cursor
        terminal.cursor = (terminal.rows, 1)
        terminal.clear_line()
        reply = input(prompt)
        terminal.cursor = cursor_save
        return reply

    def read_file_dialog(self, terminal):
        self._filename = self._get_input(terminal, 'Read filename: ')
        self.read(self._filename)

    def write_file_dialog(self, terminal):
        if (self._filename):
            prompt = 'Write filename [{}]: '.format(self._filename)
            filename = self._get_input(terminal, prompt)
            if (filename != ''):
                self._filename = filename
        else:
            prompt = 'Write as filename: '
            self._filename = self._get_input(terminal, prompt)
        self.write(self._filename)
        
    def visual(self):
        """
        Navigate and edit buffer based on user input.
        """
        terminal = ANSI()
        self.print(0, terminal.rows - 1, terminal.cols)

        buffer_line_start = 0
        while (True):
            ch = terminal.get_key()
            if (ch == 'CUF'):
                cursor_row, cursor_col = terminal.cursor
                cursor_col += 1
                if (cursor_col > terminal.cols):
                    cursor_col = terminal.cols
                terminal.cursor = cursor_row, cursor_col
            elif (ch == 'CUB'):
                cursor_row, cursor_col = terminal.cursor
                cursor_col -= 1
                if (cursor_col < 1):
                    cursor_col = 1
                terminal.cursor = cursor_row, cursor_col
            elif (ch == 'CUU'):
                cursor_row, cursor_col = terminal.cursor
                cursor_row -= 1
                if (cursor_row < 1):
                    cursor_row = 1
                terminal.cursor = cursor_row, cursor_col
            elif (ch == 'CUD'):
                cursor_row, cursor_col = terminal.cursor
                cursor_row += 1
                if (cursor_row > terminal.rows):
                    cursor_row = terminal.rows
                terminal.cursor = cursor_row, cursor_col
            elif (ch == 'PgDn' or ch == '^D'):
                buffer_line_start += terminal.rows
                if (buffer_line_start > len(self._buffer)):
                    buffer_line_start = len(self._buffer)
                cursor_save = terminal.cursor
                terminal.clear(clear_scrollback=True)
                self.print(buffer_line_start, buffer_line_start + terminal.rows - 1)
                terminal.cursor = cursor_save
            elif (ch == 'PgUp' or ch == '^U'):
                buffer_line_start -= terminal.rows
                if (buffer_line_start < 0):
                    buffer_line_start = 0
                cursor_save = terminal.cursor
                terminal.clear(clear_scrollback=True)
                self.print(buffer_line_start, buffer_line_start + terminal.rows - 1)
                terminal.cursor = cursor_save
            elif (ch == '^R'):
                self.read_file_dialog(terminal)
            elif (ch == '^W'):
                self.write_file_dialog(terminal)
            elif (ch == '^X'):
                break
            else:
                stdout.write(ch)
