from sys import stdout

class TextBuffer:
    def __init__(self, filename=None):
        self._buffer = []
        self._filename = ''
        if (filename != None):
            self._filename = filename
            self.load(filename)
        self._is_dirty = False

    def __str__(self):
        return '\n'.join(self._buffer)    

    def insert_line(self, line_num, text):
        """
        Add a line of text to the buffer after the indicated
        line number. (Lines start from 1)
        """
        if (line_num < 1):  # text buffer lines are one-based
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
        Purge the line in the buffer indicated by the 1-based line number.
        """
        buffer_index = line_num - 1
        del self._buffer[buffer_index]
        self._is_dirty = True
        
    def _read_file_line(self, file):
        """
        Read a file a line at a time, yeilding lines to reduce memory requirements.

        Args:
            file (object): the file handle returned by open()
        Returns:
            bytes: a line of the file until the file ends, then nothing
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
            self._filename = filename
        except Exception as ex:
            self._filename = ''
            print(ex)

    def save(self, filename=None, eol_marker='\n'):
        """
        Serialize contents of buffer to filename by adding end of line character(s).
        """
        if (filename == None):
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

