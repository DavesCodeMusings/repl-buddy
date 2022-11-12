from text_buffer import TextBuffer
from sys import stdout

class Atto(TextBuffer):
    cmd_prompt = '*'
    text_prompt = '>'

    def help(self):
        """
        Display brief summary of available commands
        """
        print('Editor Commands')
        print('-----------------------------------------------')
        print('{addr}a               Append new line(s) after')
        print('{addr}c               Change (replace)')
        print('[{addr1}][,{addr2}]d  Delete line(s)')
        print('{addr}i               Insert new line before')
        print('[{addr1}][,{addr2}]n  Print with numbered lines')
        print('[{addr1}][,{addr2}]p  Print')
        print('q                     Quit')


    def append(self, **kwargs):
        line_num = kwargs.get('start') or len(self._buffer)
        while (True):
            text = input(self.text_prompt)
            if (text == '.'):
                break
            line_num += 1
            self.insert_line(line_num, text)
                    

    def change(self, **kwargs):
        line_num = kwargs.get('start')
        if (line_num == None):
            return False
        text = input(self.text_prompt)
        self.update_line(line_num, text)


    def delete(self, **kwargs):
        """
        Remove a range of lines from the buffer.
        """
        start = kwargs.get('start')
        stop = kwargs.get('stop')

        if (start == None or start > len(self._buffer)):
            return False
        if (stop == None or stop > len(self._buffer)):
            return False

        line_num = start
        while (line_num <= stop):
            self.delete_line(start)  # Not a mistake
            line_num += 1


    def insert(self, **kwargs):
        line_num = kwargs.get('start') or len(self._buffer)
        if (line_num == None):
            return false
        text = input(self.text_prompt)
        
        while (True):
            text = input(self.text_prompt)
            if (text == '.'):
                break
            self.insert_line(line_num, text)
            line_num += 1
                    

    def number(self, **kwargs):
        """
        Print the buffer with line numbers.
        """
        start = kwargs.get('start') or 1
        stop = kwargs.get('stop') or len(self._buffer) - 1

        if (start > len(self._buffer) or stop > len(self._buffer)):
            return False

        if (stop < 10):
            line_num_field = '{:>1d} '
        elif (stop < 100):
            line_num_field = '{:>2d} '
        elif (stop < 1000):
            line_num_field = '{:>3d} '
        else:
            line_num_field = '{:>4d} '

        line_num = start
        while (line_num <= stop):
            stdout.write(line_num_field.format(line_num))
            stdout.write(self.get_line(line_num) + '\n')
            line_num += 1


    def print(self, **kwargs):
        """
        Display a range of buffer lines, possibly truncated to fit.
        """
        start = kwargs.get('start') or 1
        stop = kwargs.get('stop') or len(self._buffer)
        line_length = kwargs.get('line_length')

        if (start > len(self._buffer) or stop > len(self._buffer)):
            return False

        line_num = start
        while (line_num <= stop):
            if (line_length == None):
                stdout.write(self.get_line(line_num) + '\n')
            else:
                stdout.write(self.get_line(line_num)[:line_length] + '\n')
            line_num += 1


    def edit(self):
        """
        Use interactive commands to modify the text buffer.
        """
        command_functions = {}
        command_functions['a'] = self.append
        command_functions['c'] = self.change
        command_functions['d'] = self.delete
        command_functions['h'] = self.help
        command_functions['i'] = self.insert
        command_functions['n'] = self.number
        command_functions['p'] = self.print

        while (True):
            command_string = input(self.cmd_prompt)
            command_string = command_string.lower()
            if (command_string == 'q!'):
                break
            elif (command_string == 'q'):
                if (self._is_dirty == True):
                    print('Unsaved changes exist. Enter q! to override')
                else:
                    break
            else:
                cmd = command_string[-1]
                if (cmd not in command_functions):
                    print('Unrecognized command. Try ? for help.')
                elif (len(command_string) == 1):
                    result = command_functions[cmd]()
                else:
                    address = command_string[:-1]
                    address = address.replace('%', '1,$')
                    address = address.replace('$', str(len(self._buffer)))
                    if (',' in address):
                        start, stop = address.split(',')
                    else:
                        start = address
                        stop = start

                    result = command_functions[cmd](start=int(start), stop=int(stop))
                    if (result == False):
                        print('Bad address range.')

