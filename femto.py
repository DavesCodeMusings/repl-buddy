from sys import stdin, stdout
from select import poll, POLLIN
from ansi import ANSI

class Femto:
    CTRL_R = '\x12'
    CTRL_W = '\x17'
    CTRL_X = '\x18'

    def __init__(self, filename=None):
        self.buffer = ''
        self.filename = ''
        if (filename != None):
            self.read(filename)

    def read(self, filename):
        try:
            with open(filename) as f:
                self.buffer = f.readlines()
            self.filename = filename
        except Exception as ex:
            self.filename = ''
            print(ex)

    def dump(self):
        for line in self.buffer:
            stdout.write(line)

    def purge(self):
        del self.buffer
        self.buffer = ''

    def page(self, page_length=20):
        line_num = 1
        for line in self.buffer:
            if (line_num % page_length == 0):
                ch = stdin.read(1)
                if (ch == 'q' or ch == 'Q'):
                    break
            stdout.write(line)
            line_num += 1
            
    def write(self, filename=None):
        if (filename == None):
            filename = self.filename
        with open(filename, 'w') as f:
            for line in self.buffer:
                f.write(line)

    def _show_status(self, terminal, message):
        cursor_save = terminal.cursor
        terminal.cursor = (terminal.rows, 1)
        terminal.style = ANSI.INVERSE
        message += ' ' * (terminal.cols - len(message))  # pad to fill terminal width
        stdout.write(message)
        terminal.style = ANSI.NORMAL
        terminal.cursor = cursor_save

    def visual(self):
        terminal = ANSI()

        line_num = 1
        for line in self.buffer:
            if (line_num > terminal.rows):
                break
            stdout.write(line[:terminal.cols])
            line_num += 1

        commands = 'CTRL+R Read  CTRL+W Write  CTRL+X Exit'
        padding = ' ' * (terminal.cols - len(commands) - len(self.filename))
        self._show_status(terminal, commands + padding + self.filename)

        poll_obj = poll()
        poll_obj.register(stdin, POLLIN)
        while (True):
            ch = stdin.read(1) if poll_obj.poll(1) else None
            if (ch != None):
                if (ch == Femto.CTRL_X):
                    break
                elif (ch == Femto.CTRL_W):
                    self.write()
                else:
                    stdout.write(ch)
