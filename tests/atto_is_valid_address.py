import unittest
from atto import Atto

class TestAttoIsValidAddr(unittest.TestCase):
    def __init__(self):
        self.e = Atto()
        self.e._buffer = {
            'How are you gentlemen?',
            'All your base are belong to us!',
            'You are on the way to destruction.',
            'You have no chance to survive. Make your time.'
        }
        self.e._current_line = len(self.e._buffer)

    def test_is_valid_start_addr(self):
        self.assertFalse(self.e._is_valid_addr(-1, None, None))
        self.assertFalse(self.e._is_valid_addr(0, None, None))
        self.assertTrue(self.e._is_valid_addr(0, None, None, zero_start_ok=True))
        self.assertTrue(self.e._is_valid_addr(1, None, None))
        self.assertFalse(self.e._is_valid_addr(5, None, None))
        
    def test_is_valid_stop_addr(self):
        self.assertFalse(self.e._is_valid_addr(1, -1, None))
        self.assertFalse(self.e._is_valid_addr(1, 0, None))
        self.assertTrue(self.e._is_valid_addr(1, 1, None))
        self.assertFalse(self.e._is_valid_addr(1, 5, None))
        self.assertFalse(self.e._is_valid_addr(2, 1, None))

    def test_is_valid_dest_addr(self):
        self.assertFalse(self.e._is_valid_addr(2, 3, -1))
        self.assertTrue(self.e._is_valid_addr(2, 3, 0))
        self.assertTrue(self.e._is_valid_addr(2, 3, 1))
        self.assertFalse(self.e._is_valid_addr(2, 3, 2))
        self.assertFalse(self.e._is_valid_addr(2, 3, 3))
        self.assertTrue(self.e._is_valid_addr(2, 3, 4))
        self.assertFalse(self.e._is_valid_addr(2, 3, 5))

if __name__ == '__main__':
    unittest.main()
