# atto
#    (combining form) a metric system unit prefix denoting 10 to the -18 power
#    (noun) a tiny line-based text editor modeled as a subset of the ed editor

from sys import stdout

class TextBuffer:
    """
    Functions for loading, saving and manipulating text editor buffers.
    """
    def __init__(self, filename=None):
        self._buffer = []
        self._filename = ''
        if filename != None:
            self._filename = filename
            self.load(filename)
        self._is_dirty = False

    def __str__(self):
        return '\n'.join(self._buffer)    

    def insert_line(self, line_num, text):
        """
        Add a line of text to the buffer after the indicated line number.
        (Lines start from 1)
        """
        if line_num < 1:  # text buffer lines are one-based
            return False
        buffer_index = line_num - 1
        self._buffer.insert(buffer_index, text.rstrip('\r\n'))
        self._is_dirty = True

    def get_line(self, line_num):
        """
        Retrieve the line indicated by line number.
        """
        buffer_index = line_num - 1
        return self._buffer[buffer_index]

    def update_line(self, line_num, text):
        """
        Replace the line indicated by the line number with new text.
        """
        buffer_index = line_num - 1
        self._buffer[buffer_index] = text.rstrip('\r\n')
        self._is_dirty = True

    def delete_line(self, line_num):
        """
        Purge the line in the buffer indicated by the line number.
        """
        buffer_index = line_num - 1
        del self._buffer[buffer_index]
        self._is_dirty = True
        
    def _read_file_line(self, file):
        """
        Read from a file one line at a time, yeilding lines to reduce
        memory impact.
        """
        while True:
            line = file.readline()
            if line:
                yield line
            else: # empty line means end of the file
                return

    def load(self, filename):
        """
        Read file contents into buffer while stripping end of line characters.
        """
        try:
            with open(filename, 'r') as file:
                for line in self._read_file_line(file):
                    self._buffer.append(line.rstrip('\r\n'))
            self._is_dirty = True
        except:
            pass
            self._filename = filename

    def save(self, filename=None, eol_marker='\n'):
        """
        Write contents of buffer to filename by adding end of line character(s).
        """
        if filename == None:
            filename = self._filename
        with open(filename, 'w') as f:
            for line in self._buffer:
                f.write(line + eol_marker)
        self._is_dirty = False

    def purge(self):
        """
        Release the buffer list object and start with a fresh one.
        """
        del self._buffer
        self._buffer = []
        self._is_dirty = False


class Atto(TextBuffer):
    """
    A primitive line editor, with a subset of ed editor functionality.
    """
    cmd_prompt = '*'
    text_prompt = '>'

    def help(self):
        """
        Display brief usage summary
        """
        help_text = '\n'.join([
            'Usage: {addr}cmd',
            '',
            'Line Addressing',
            '-------------------------',
            '{n}        single line',
            '{n1},{n2}  range of lines',
            '1          first line',
            '.          current line',
            '$          last line',
            '%          all lines 1,$',
            '',
            'Command Summary',
            '--------------------------------------',
            '{n}a        Append new line(s) after',
            '{n}c        Change (replace) line',
            '{n1},{n2}d  Delete line(s)',
            'f           View/change filename',
            '{n}i        Insert new line before',
            '{n1},{n2}n  Print with numbered lines',
            '{n1},{n2}p  Print',
            'q           Quit',
            'q! or Q     Quit without saving'
            'w           Write (save) to file'
        ])
        print(help_text)

    def prompt_filename(self):
        """
        Prompt for filename, accepting current name as the default value.
        """
        filename = input('[{}]:'.format(self._filename))
        if filename != '':
            self._filename = filename

    def _input_multiline(self, prompt):
        """
        Yield user input as lines until a single . is encountered.
        """
        while True:
            text = input(prompt)
            if text != '.':
                yield text
            else:
                return

    def append(self, **kwargs):
        """
        Add new lines after the indicated line number.
        """
        line_num = kwargs.get('start') or len(self._buffer)
        if line_num == None or line_num < 0:
            return False
        for line in self._input_multiline(self.text_prompt):
            line_num += 1
            self.insert_line(line_num, line)
        self._current_line = line_num

    def change(self, **kwargs):
        """
        Replace line with new line.
        """
        line_num = kwargs.get('start')
        if line_num == None:
            return False
        text = input(self.text_prompt)
        self.update_line(line_num, text)

    def delete(self, **kwargs):
        """
        Remove a range of lines from the buffer.
        """
        start = kwargs.get('start')
        stop = kwargs.get('stop')
        if start == None or start > len(self._buffer):
            return False
        if stop == None or stop > len(self._buffer):
            return False
        line_num = start
        while line_num <= stop:
            self.delete_line(start)  # Not a mistake
            line_num += 1
        self._current_line = start

    def edit(self, **kwargs):
        """
        Load a new file into the buffer.
        """
        if self._is_dirty == True:
            print('Unsaved changes exist. Use uppercase E to override')
        else:
            self.prompt_filename()
            self.purge()
            self.load(self._filename)
            self._is_dirty = False
            self._current_line = len(self._buffer) or 1

    def edit_unconditional(self, **kwargs):
        """
        Load a new file into the buffer, disregarding unsaved changes.
        """
        self._is_dirty = False
        self.edit()

    def insert(self, **kwargs):
        """
        Add new lines after the indicated line number.
        """
        line_num = kwargs.get('start')
        if line_num == None or line_num < 1:
            return False
        for line in self._input_multiline(self.text_prompt):
            self.insert_line(line_num, line)
            line_num += 1
        self._current_line = line_num - 1

    def join(self, **kwargs):
        """
        Combine lines.
        """
        start = kwargs.get('start') or self._current_line
        stop = kwargs.get('stop') or self._current_line
        if start > len(self._buffer) or stop > len(self._buffer):
            return False
        self._buffer[start-1:stop] = [''.join(self._buffer[start-1:stop])]

    def number(self, **kwargs):
        """
        Print lines prefixed with line numbers.
        """
        start = kwargs.get('start') or self._current_line
        stop = kwargs.get('stop') or self._current_line
        if start > len(self._buffer) or stop > len(self._buffer):
            return False
        if stop < 10:
            line_num_field = '{:>1d} '
        elif stop < 100:
            line_num_field = '{:>2d} '
        elif stop < 1000:
            line_num_field = '{:>3d} '
        else:
            line_num_field = '{:>4d} '
        line_num = start
        while line_num <= stop:
            stdout.write(line_num_field.format(line_num))
            stdout.write(self.get_line(line_num) + '\n')
            line_num += 1

    def print(self, **kwargs):
        """
        Display a range of buffer lines, possibly truncated to fit.
        """
        start = kwargs.get('start') or self._current_line
        stop = kwargs.get('stop') or self._current_line
        line_length = kwargs.get('line_length')
        if start > len(self._buffer) or stop > len(self._buffer):
            return False
        line_num = start
        while line_num <= stop:
            if line_length == None:
                stdout.write(self.get_line(line_num) + '\n')
            else:
                stdout.write(self.get_line(line_num)[:line_length] + '\n')
            line_num += 1

    def write(self):
        """
        Save the buffer to a file.
        """
        self.prompt_filename()
        self.save(self._filename)

    def begin(self):
        """
        Use interactive commands to modify the text buffer.
        """
        cmd_functions = {}
        cmd_functions['?'] = self.help
        cmd_functions['a'] = self.append
        cmd_functions['c'] = self.change
        cmd_functions['d'] = self.delete
        cmd_functions['e'] = self.edit
        cmd_functions['E'] = self.edit_unconditional
        cmd_functions['f'] = self.prompt_filename
        cmd_functions['i'] = self.insert
        cmd_functions['j'] = self.join
        cmd_functions['n'] = self.number
        cmd_functions['p'] = self.print
        cmd_functions['w'] = self.write

        self._current_line = len(self._buffer) or 1

        while True:
            cmd_string = input(self.cmd_prompt)
            if cmd_string == 'q!' or cmd_string == 'Q':
                break
            elif cmd_string == 'q':
                if self._is_dirty == True:
                    print('Unsaved changes exist. Use uppercase Q to override')
                else:
                    break
            else:
                cmd = cmd_string[-1]
                if cmd not in cmd_functions:
                    print('Unrecognized cmd. Try ? for help.')
                elif len(cmd_string) == 1:
                    result = cmd_functions[cmd]()
                    if result == False:
                        print('Bad address.')
                else:
                    address = cmd_string[:-1]
                    address = address.replace('%', '1,$')
                    address = address.replace('.', str(self._current_line))
                    address = address.replace('$', str(len(self._buffer)))
                    if ',' in address:
                        start, stop = address.split(',')
                    else:
                        start = address
                        stop = start
                    result = cmd_functions[cmd](start=int(start), stop=int(stop))
                    if result == False:
                        print('Bad address range.')

def atto(filename=None):
    editor = Atto(filename)
    print('Enter ? to view help.')
    editor.begin()
