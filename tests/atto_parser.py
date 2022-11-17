import unittest
from random import randint
from atto import Atto

class TestAttoParser(unittest.TestCase):
    def __init__(self):
        self.e = Atto()
        self.e._buffer = [
            'How are you gentlemen?',
            'All your base are belong to us!',
            'You are on the way to destruction.',
            'You have no chance to survive. Make your time.'
        ]
        self.e._current_line = len(self.e._buffer)

    def test_single_addr_only(self):
        test_addr = randint(1,99)
        cmd_string = '{:d}'.format(test_addr)
        addr1, addr2, cmd, param = self.e.parse(cmd_string)
        self.assertEqual(addr1, test_addr)
        self.assertEqual(addr2, None)
        self.assertEqual(cmd, 'p')
        self.assertEqual(param, '')

    def test_addr_range_only(self):
        test_addr1 = randint(1,50)
        test_addr2 = randint(51,100)
        cmd_string = '{:d},{:d}'.format(test_addr1, test_addr2)
        addr1, addr2, cmd, param = self.e.parse(cmd_string)
        self.assertEqual(addr1, test_addr1)
        self.assertEqual(addr2, test_addr2)
        self.assertEqual(cmd, 'p')
        self.assertEqual(param, '')

    def test_regex_addr_only(self):
        addr1, addr2, cmd, param = self.e.parse('/All')
        self.assertEqual(addr1, 2)
        self.assertEqual(addr2, None)
        self.assertEqual(cmd, 'p')
        self.assertEqual(param, '')
        addr1, addr2, cmd, param = self.e.parse('/you')
        self.assertEqual(addr1, 4)
        self.assertEqual(addr2, None)
        self.assertEqual(cmd, 'p')
        self.assertEqual(param, '')

    def test_cmd_only(self):
        self.assertEqual(self.e.parse('f'), (None, None, 'f', ''))

    def test_cmd_param(self):
        self.assertEqual(self.e.parse('e file1.txt'), (None, None, 'e', 'file1.txt'))

    def test_cmd_param_no_space(self):
        self.assertEqual(self.e.parse('wfile2.txt'), (None, None, 'w', 'file2.txt'))

    def test_single_addr_cmd(self):
        addr = randint(1,99)
        cmd_string = '{:d}i'.format(addr)
        self.assertEqual(self.e.parse(cmd_string), (addr, None, 'i', ''))

    def test_addr_range_cmd(self):
        addr1 = randint(1,50)
        addr2 = randint(51,100)
        cmd_string = '{:d},{:d}n'.format(addr1, addr2)
        self.assertEqual(self.e.parse(cmd_string), (addr1, addr2, 'n', ''))

    def test_regex_with_cmd(self):
        addr1, addr2, cmd, param = self.e.parse('/gentlemen/n')
        self.assertEqual(addr1, 1)
        self.assertEqual(addr2, None)
        self.assertEqual(cmd, 'n')
        self.assertEqual(param, '')

    def test_addr_range_cmd_param(self):
        addr1 = randint(1, 50)
        addr2 = randint(51, 100)
        addr3 = randint(101, 150)
        cmd_string = '{:d},{:d}m{:d}'.format(addr1, addr2, addr3)
        self.assertEqual(self.e.parse(cmd_string), (addr1, addr2, 'm', addr3))

    def test_dollar_addr(self):
        cmd_string = '2,$p'
        self.assertEqual(self.e.parse(cmd_string), (2, len(self.e._buffer), 'p', ''))

    def test_dollar_param(self):
        cmd_string = '1,2t$'
        self.assertEqual(self.e.parse(cmd_string), (1, 2, 't', len(self.e._buffer)))

    def test_percent_param(self):
        addr1 = randint(1, 50)
        addr2 = randint(51, 100)
        cmd_string = '{:d},{:d}m%'.format(addr1, addr2)  # % as destination is invalid
        self.assertEqual(self.e.parse(cmd_string), (addr1, addr2, 'm', '%'))

if __name__ == '__main__':
    unittest.main()
