from sys import stdin, stdout, exit
from ansi import ANSI
from text_buffer import TextBuffer

class Femto(TextBuffer):
    KEY_CTRL_N = 0x0E
    KEY_CTRL_R = 0x12
    KEY_CTRL_W = 0x17
    KEY_CTRL_X = 0x18

    def _set_title(self, msg):
        """
        Show message on the top line in dimmed color.
        """
        self.terminal.cursor.save()
        col = int((self.terminal.cols - len(msg)) / 2)
        self.terminal.cursor.coord = (1, col)
        self.terminal.clear_line()
        self.terminal.style = ANSI.DIM
        stdout.write(msg)
        self.terminal.cursor.restore()

    def _set_status(self, msg):
        """
        Show message on the bottom line in dimmed color.
        """
        self.terminal.cursor.save()
        self.terminal.cursor.coord = (self.terminal.lines, 0)
        self.terminal.clear_line()
        self.terminal.style = ANSI.DIM
        stdout.write(msg)
        self.terminal.cursor.restore()

    def _get_input(self, prompt):
        """
        Show prompt and capture user reply.
        """
        self.terminal.cursor.save()
        self.terminal.cursor.coord = (self.terminal.lines, 1)
        self.terminal.clear_line()
        self.terminal.style = ANSI.BOLD
        stdout.write(prompt)
        self.terminal.style = ANSI.NORMAL
        reply = input()
        self.terminal.cursor.restore()
        return reply

    def _show_coords(self):
        current_cursor = str(self.terminal.cursor)
        self.terminal.cursor.save()
        self.terminal.cursor.hide()
        self.terminal.cursor.coord = (self.terminal.lines, self.terminal.cols-16)
        self.terminal.clear_line(before_cursor=False, after_cursor=True)
        self.terminal.style = ANSI.DIM
        stdout.write(current_cursor)
        self.terminal.style = ANSI.NORMAL
        self.terminal.cursor.restore()
        self.terminal.cursor.show()

    def _refresh_screen(self):
        self.terminal.clear(clear_scrollback=True)
        self._set_title(self.filename or '(none)')
        self.terminal.cursor.coord = (2,1)
        for line_num in range(1, self.terminal.lines-1):
            line = self.get_line(line_num)
            if (line != None):
                stdout.write(line)
                if line_num < self.terminal.lines - 2:
                    stdout.write('\n')
        self._set_status('[^N]ew [^R]ead [^W]rite e[^X]it')
        self._show_coords()

    def _new_buffer_dialog(self):
        if (self._buffer != ''):
            prompt = 'Clear buffer [y/N]? '
            confirm = self._get_input(prompt)
            if (confirm == 'y' or confirm == 'Y'):
                self.purge()
            self.filename = ''
            self._refresh_screen()

    def _read_file_dialog(self):
        self.filename = self._get_input('Read filename: ')
        self.load(self.filename)
        self._refresh_screen()

    def _write_file_dialog(self):
        if (self.filename):
            prompt = 'Write filename [{}]: '.format(self.filename)
            filename = self._get_input(prompt)
            if (filename != ''):
                self.filename = filename
        else:
            while (self.filename == ''):
                prompt = 'Write as filename: '
                self.filename = self._get_input(prompt)
        self.save(self.filename)
        self._refresh_screen()

    def _exit_dialog(self):
        if (self._buffer != ''):
            prompt = 'Exit [y/N]? '
            confirm = self._get_input(prompt)
            if (confirm == 'y' or confirm == 'Y'):
                del self.terminal.scroll_region
                self.terminal.clear(clear_scrollback=True)
                self.terminal.cursor.coord = (1,1)
                exit(0)
            else:
                self._refresh_screen()
                return False

    def cursor_move(self, key_code):
        cursor_row, cursor_col = self.terminal.cursor.coord
        if key_code == ANSI.KEY_RIGHT:
            cursor_col +=1
        elif key_code == ANSI.KEY_LEFT:
            cursor_col -=1
        elif key_code == ANSI.KEY_DOWN:
            cursor_row +=1
        elif key_code == ANSI.KEY_UP:
            cursor_row -=1
        cursor_row = max(cursor_row, 2)  # Row 1 is title bar
        cursor_row = min(cursor_row, self.terminal.lines - 1)  # Last row is status bar
        cursor_col = max(cursor_col, 1)
        cursor_col = min(cursor_col, self.terminal.cols)
        self.terminal.cursor.coord = cursor_row, cursor_col
        self._show_coords()

    def screen_scroll(self, key_code):
        if key_code == ANSI.KEY_NPAGE:
            self._current_line += (self.terminal.lines - 2)
        elif key_code == ANSI.KEY_PPAGE:
            self._current_line -= (self.terminal.lines - 2)
        self._current_line = max(self._current_line, 1)
        self._current_line = min(self._current_line, len(self._buffer))
        self._refresh_screen()
        self._show_coords()

    def begin(self):
        """
        Navigate and edit buffer based on user input.
        """
        self.terminal = ANSI()
        self.terminal.echo = False
        self.terminal.scroll_region = (2, 23)
        self._current_line = len(self._buffer) or 1
        self._refresh_screen()

        ctrl_key_functions = {
            Femto.KEY_CTRL_N: self._new_buffer_dialog,
            Femto.KEY_CTRL_R: self._read_file_dialog,
            Femto.KEY_CTRL_W: self._write_file_dialog,
            Femto.KEY_CTRL_X: self._exit_dialog
        }

        while True:
            key_code = self.terminal.getch()
            if key_code > 0x1F and key_code < 0x7F:
                stdout.write(chr(key_code))
            elif key_code == ANSI.KEY_ENTER:
                self.terminal.next_line()
            elif key_code >= ANSI.KEY_DOWN and key_code <= ANSI.KEY_BACKSPACE:
                self.cursor_move(key_code)
            elif key_code == ANSI.KEY_PPAGE or key_code == ANSI.KEY_NPAGE:
                self.screen_scroll(key_code)
            elif key_code in ctrl_key_functions:
                ctrl_key_functions[key_code]()
