# atto
#   (combining form) a metric system unit prefix denoting 10 to the -18 power
#   (noun) a tiny line-based text editor modeled as a subset of the ed editor

from sys import stdout, exit

class TextBuffer:
    """
    Functions for loading, saving and manipulating text editor buffers.
    Lines start from 1 (not 0) to be consistent with editor numbering.
    """
    def __init__(self, filename=None):
        self._buffer = []
        self._is_dirty = False
        self.verbose = True
        self.filename = filename
        if filename != None:
            self.load(filename)

    def __str__(self):
        return '\n'.join(self._buffer)    

    def insert_line(self, line_num, text):
        """
        Add a line of text to the buffer at the indicated line number.
        Existing lines are pushed down to make room.
        """
        if line_num < 1:
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

    def copy_range(self, start, stop, dest):
        """
        Copy lines start..stop after line given by dest.
        """
        self._buffer[dest:dest] = self._buffer[start-1:stop]
        self._is_dirty = True

    def delete_range(self, start, stop):
        """
        Remove the lines from start..stop.
        """
        del self._buffer[start-1:stop]
        self.is_dirty = True

    def move_range(self, start, stop, dest):
        """
        Like copy, but remove the source range.
        """
        self.copy_range(start, stop, dest)
        offset = stop - start + 1 if (dest < start) else 0
        self.delete_range(start+offset, stop+offset)
        self.is_dirty = True
        
    def _read_file_line(self, file_handle):
        """
        Read from a file one line at a time, yeilding lines to reduce
        memory impact. Used by load.
        """
        while True:
            line = file_handle.readline()
            if line:
                yield line
            else: # empty line means end of the file
                return

    def load(self, filename):
        """
        Read file contents into buffer while stripping end of line characters.
        """
        try:
            with open(filename, 'r') as f:
                for line in self._read_file_line(f):
                    self._buffer.append(line.rstrip('\r\n'))
        except Exception as ex:
            if self.verbose == True:
                stdout.write('File error: {}\n'.format(ex))
            return False
        else:
            self.filename = filename
            self._is_dirty = False
            if self.verbose == True:
                stdout.write('{:d} lines read from {:s}\n'.format(len(self._buffer), filename))
            return True

    def save(self, filename=None, eol_marker='\n'):
        """
        Write contents of buffer to filename by adding end of line character(s).
        """
        if filename == None:
            filename = self.filename
        try:
            with open(filename, 'w') as f:
                for line in self._buffer:
                    f.write(line + eol_marker)
        except Exception as ex:
            if self.verbose == True:
                stdout.write('File error: {}\n'.format(ex))
            return False
        else:
            self.filename = filename
            self._is_dirty = False
            if self.verbose == True:
                stdout.write('{:d} lines written to {:s}\n'.format(len(self._buffer), filename))
            return True

    def purge(self):
        """
        Release the buffer list object and start with a fresh one.
        """
        del self._buffer
        self._buffer = []
        self.filename = None
        self._is_dirty = False


class Atto(TextBuffer):
    """
    A primitive line editor, painfully similar to the ed editor, but
    with without the cool regex stuff.
    """
    cmd_prompt = '*'
    text_prompt = '>'

    def help(self, **kwargs):
        """
        Display brief usage summary
        """
        help_text = '\n'.join([
            'Usage: {addr}cmd',
            '',
            'Line Addressing',
            '--------------------------',
            '{n}         single line',
            '{n1},{n2}   range of lines',
            '1           first line',
            '.           current line',
            '$           last line',
            '%           all lines 1,$',
            '',
            'Command Summary',
            '---------------------------------------',
            '{n}a        Append new line(s) after',
            '{n1},{n2}c  Change (replace) line(s)',
            '{n1},{n2}d  Delete line(s)',
            'e [path]    Edit new file',
            'f [path]    View/change filename',
            '{n}i        Insert new line(s) before',
            '{n1},{n2}n  Print with numbered lines',
            '{n1},{n2}p  Print',
            'q           Quit',
            'w [path]    Write (save) buffer to file'
        ])
        stdout.write(help_text + '\n')

    def _input_multiline(self):
        """
        Yield user input as lines until a single . is encountered.
        Used by insert and append operations.
        """
        stdout.write('Enter a single . to exit input mode.\n')
        while True:
            text = input(self.text_prompt)
            if text != '.':
                yield text
            else:
                return

    def _prompt_filename(self, prompt='Filename'):
        """
        Ask for a filename offering the current one as a default value.
        """
        if self.filename != None:
            filename = input('{:s} [{:s}]: '.format(prompt, self.filename))
        else:
            filename = input('{:s}: '.format(prompt))
        return filename

    def _is_valid_addr(self, start=None, stop=None, dest=None, zero_start_ok=False):
        """
        Test if address parameters in range, non-overlapping, etc.
        """
        valid_start = 0 if (zero_start_ok == True) else 1

        if start == None:
            return False
        if start < valid_start or start > len(self._buffer):
            return False

        if stop != None:
            if stop < 1 or stop > len(self._buffer):
                return False
            if stop < start:
                return False

        if dest != None:
            if dest < 0 or dest > len(self._buffer):
                return False
            if dest >= start and dest <= stop:
                return False
            
        return True

    def append(self, **kwargs):
        """
        Add new lines after the indicated line number.
        """
        start = kwargs.get('start')
        if start == None:
            start = self._current_line
        if self._is_valid_addr(start, zero_start_ok=True) == False:
            return False

        line_num = start
        for line in self._input_multiline():
            line_num += 1
            self.insert_line(line_num, line)
        self._current_line = line_num

    def change(self, **kwargs):
        """
        Replace line(s) with new line(s).
        """
        self.delete(**kwargs)
        self.insert(**kwargs)

    def delete(self, **kwargs):
        """
        Remove a range of lines from the buffer.
        """
        start = kwargs.get('start') or self._current_line
        stop = kwargs.get('stop') or start
        if self._is_valid_addr(start, stop) == False:
            return False
        self.delete_range(start, stop)
        self._current_line = start

    def edit(self, **kwargs):
        """
        Load a new file into the buffer.
        """
        if self._is_dirty == True:
            stdout.write('Unsaved changes exist. Use uppercase E to override.\n')
        else:
            filename = kwargs.get('param') or self.filename or self._prompt_filename()
            if filename != None:
                self.purge()
                self.load(filename)
                self._is_dirty = False
                self._current_line = len(self._buffer) or 1
                self.filename = filename

    def edit_unconditional(self, **kwargs):
        """
        Load a new file into the buffer, disregarding unsaved changes.
        """
        self._is_dirty = False
        self.edit(**kwargs)

    def file(self, **kwargs):
        """
        Show current filename or replace if param is present
        """
        new_name = kwargs.get('param')
        if new_name != '':
            self.filename = new_name
        else:
            stdout.write((self.filename or '(none)') + '\n')

    def insert(self, **kwargs):
        """
        Add new lines after the indicated line number.
        """
        start = kwargs.get('start') or self._current_line
        if self._is_valid_addr(start) == False:
            return False

        line_num = start
        for line in self._input_multiline():
            self.insert_line(line_num, line)
            line_num += 1
        self._current_line = line_num - 1

    def join(self, **kwargs):
        """
        Combine lines.
        """
        start = kwargs.get('start') or self._current_line
        stop = kwargs.get('stop') or self._current_line
        if self._is_valid_addr(start, stop) == False:
            return False

        self._buffer[start-1:stop] = [''.join(self._buffer[start-1:stop])]
        self._current_line = start
        self._is_dirty = True

    def move(self, **kwargs):
        """
        Like transfer but remove the source range after the copy.
        """
        start = kwargs.get('start')
        stop = kwargs.get('stop') or start
        dest = kwargs.get('param')
        if self._is_valid_addr(start, stop) == False:
            return False
        self.copy_range(start, stop, dest)
        offset = stop - start + 1 if (dest < start) else 0
        self.delete_range(start+offset, stop+offset)
        self._current_line = dest - 1 + stop - start

    def number(self, **kwargs):
        """
        Print lines prefixed with line numbers.
        """
        start = kwargs.get('start') or self._current_line
        stop = kwargs.get('stop') or start
        if self._is_valid_addr(start, stop) == False:
            return False

        if stop < 10:
            line_num_field = '{:>1d}'
        elif stop < 100:
            line_num_field = '{:>2d}'
        elif stop < 1000:
            line_num_field = '{:>3d}'
        else:
            line_num_field = '{:>4d}'

        line_num = start
        while line_num <= stop:
            stdout.write(line_num_field.format(line_num) + ' ')
            stdout.write(self.get_line(line_num) + '\n')
            line_num += 1

    def print(self, **kwargs):
        """
        Display a range of buffer lines, possibly truncated to fit.
        """
        start = kwargs.get('start') or self._current_line
        stop = kwargs.get('stop') or start
        line_length = kwargs.get('line_length')
        if self._is_valid_addr(start, stop) == False:
            return False

        line_num = start
        while line_num <= stop:
            if line_length == None:
                stdout.write(self.get_line(line_num) + '\n')
            else:
                stdout.write(self.get_line(line_num)[:line_length] + '\n')
            line_num += 1

    def quit(self, **kwargs):
        if self._is_dirty == False or kwargs.get('param') == '!':
            self.quit_unconditional()
        else:
            stdout.write('Unsaved changes exist. Use uppercase Q to override.\n')

    def quit_unconditional(self, **kwargs):
        del self._buffer
        exit(0)

    def show_current_line(self, **kwargs):
        stdout.write(str(self._current_line) + '\n')

    def toggle_verbosity(self, **kwargs):
        self.verbose = not self.verbose
        state = 'on' if self.verbose else 'off'
        stdout.write('Verbose messages: {}\n'.format(state))

    def transfer(self, **kwargs):
        """
        Copy lines start..stop to the line after dest.
        """
        start = kwargs.get('start')
        stop = kwargs.get('stop') or start
        dest = kwargs.get('param')
        if self._is_valid_addr(start, stop) == False:
            return False
        self.copy_range(start, stop, dest)
        self._current_line = dest + stop - start + 1

    def write(self, **kwargs):
        """
        Save the buffer to a file.
        """
        filename = kwargs.get('param') or self.filename or self._prompt_filename()
        if (filename):
            result = self.save(filename)
            if (result == False):
                stdout.write('Write failed!\n')

    def parse(self, cmd_string):
        """
        Split a command string into address range, command, and parameter.
        """
        if (cmd_string == None or cmd_string == ''):
            return None, None, None, None

        cmd_location = 0
        for ch in cmd_string:
            if ch not in '0123456789$%,':  # all valid address range chars
                break
            cmd_location += 1

        if cmd_location == 0:
            addr1 = None
            addr2 = None
        else:
            addr_range = cmd_string[0:cmd_location]
            addr_range = addr_range.replace('%', '1,$')
            addr_range = addr_range.replace('.', str(self._current_line))
            addr_range = addr_range.replace('$', str(len(self._buffer)))
            if ',' in addr_range:
                addr1 = int(addr_range.split(',')[0])
                addr2 = int(addr_range.split(',')[1])
            else:
                addr1 = int(addr_range)
                addr2 = None

        cmd = cmd_string[cmd_location:cmd_location+1]
        if cmd == '':  # mimic ed's behavior
            cmd = 'p'  # printing only end of addr range
            addr1 = addr2 or addr1
            addr2 = addr1

        param = cmd_string[cmd_location+1:].strip()
        if param.isdigit() == True:
            param = int(param)
        elif param == '.':
            param = self._current_line
        elif param == '$':
            param = len(self._buffer)

        return addr1, addr2, cmd, param

    def begin(self):
        """
        Use interactive commands to modify the text buffer.
        """
        cmd_functions = {
            '?': self.help,
            '=': self.show_current_line,
            'a': self.append,
            'c': self.change,
            'd': self.delete,
            'e': self.edit,
            'E': self.edit_unconditional,
            'f': self.file,
            'H': self.toggle_verbosity,
            'i': self.insert,
            'j': self.join,
            'm': self.move,
            'n': self.number,
            'p': self.print,
            'q': self.quit,
            'Q': self.quit_unconditional,
            't': self.transfer,
            'w': self.write
        }

        self._current_line = len(self._buffer) or 1

        while True:
            cmd_string = input(self.cmd_prompt)
            addr1, addr2, cmd, param = self.parse(cmd_string)
            if cmd not in cmd_functions:
                stdout.write('Unrecognized cmd. Try ? for help.\n')
            else:
                result = cmd_functions[cmd](start=addr1, stop=addr2, param=param)
                if result == False:
                    stdout.write('Bad address range.\n')

def atto(filename=None):
    editor = Atto(filename)
    editor.begin()
