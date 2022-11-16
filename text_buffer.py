from sys import stdout

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
