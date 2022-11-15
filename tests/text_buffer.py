import unittest
from atto import TextBuffer

class TestTextBuffer(unittest.TestCase):
    def __init__(self):
        self.b = TextBuffer()

    def test_instantiatiation(self):
        self.assertEqual(self.b._buffer, [])
        self.assertEqual(self.b._is_dirty, False)
        self.assertEqual(self.b.filename, None)
        self.assertEqual(self.b.__str__(), '')
    
    def test_insert_line(self):
        self.b.insert_line(1, 'World')
        self.assertEqual(self.b._buffer[0], 'World')
        self.b.insert_line(1, 'Hello')
        self.assertEqual(self.b._buffer[0], 'Hello')
        self.assertEqual(self.b._buffer[1], 'World')
        self.assertEqual(self.b._is_dirty, True)

    def test_get_line(self):
        self.assertEqual(self.b.get_line(1), self.b._buffer[0])
        self.assertEqual(self.b.get_line(2), self.b._buffer[1])
        self.assertEqual(self.b._is_dirty, True)

    def test_update_line(self):
        self.b.update_line(1, 'We are all one')
        self.assertEqual(self.b._buffer[0], 'We are all one')
        self.assertEqual(self.b._buffer[1], 'World')
        self.assertEqual(self.b._is_dirty, True)
        
    def test_delete_line(self):
        self.b.delete_line(1)
        self.assertEqual(self.b._buffer[0], 'World')
        self.assertEqual(self.b._is_dirty, True)

    def test_save(self):
        self.b.save('/tests/text_buffer_temp.txt')
        self.assertEqual(self.b._is_dirty, False)

    def test_load(self):
        b2 = TextBuffer()
        b2.load('/tests/text_buffer_temp.txt')
        self.assertEqual(b2._buffer[0], self.b._buffer[0])
        self.assertEqual(b2._is_dirty, False)

    def test_purge(self):
        self.b.purge()
        self.assertEqual(self.b._buffer, [])
        self.assertEqual(self.b._is_dirty, False)
        self.assertEqual(self.b.filename, None)
        self.assertEqual(self.b.__str__(), '')

if __name__ == '__main__':
    unittest.main()
