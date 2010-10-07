import helper

import sys
import unittest
import opsutils

class ModeBitsTestCase(unittest.TestCase):

    def test_default(self):
        b = opsutils._ModeBits()
        self.assertEqual(b.read, None)
        self.assertEqual(b.write, None)
        self.assertEqual(b.execute, None)

    def test_seven(self):
        b = opsutils._ModeBits(7)
        self.assertTrue(b.read)
        self.assertTrue(b.write)
        self.assertTrue(b.execute)

    def test_six(self):
        b = opsutils._ModeBits(6)
        self.assertTrue(b.read)
        self.assertTrue(b.write)
        self.assertFalse(b.execute)

    def test_five(self):
        b = opsutils._ModeBits(5)
        self.assertTrue(b.read)
        self.assertFalse(b.write)
        self.assertTrue(b.execute)

    def test_four(self):
        b = opsutils._ModeBits(4)
        self.assertTrue(b.read)
        self.assertFalse(b.write)
        self.assertFalse(b.execute)

    def test_three(self):
        b = opsutils._ModeBits(3)
        self.assertFalse(b.read)
        self.assertTrue(b.write)
        self.assertTrue(b.execute)

    def test_two(self):
        b = opsutils._ModeBits(2)
        self.assertFalse(b.read)
        self.assertTrue(b.write)
        self.assertFalse(b.execute)

    def test_one(self):
        b = opsutils._ModeBits(1)
        self.assertFalse(b.read)
        self.assertFalse(b.write)
        self.assertTrue(b.execute)

    def test_zero(self):
        b = opsutils._ModeBits(0)
        self.assertFalse(b.read)
        self.assertFalse(b.write)
        self.assertFalse(b.execute)

class ModeTestCase(unittest.TestCase):

    def test_default(self):
        m = opsutils.mode()

        self.assertEqual(m.user.read, None)
        self.assertEqual(m.group.write, None)
        self.assertEqual(m.other.execute, None)

    def test_get(self):
        m = opsutils.mode(0740)

        self.assertTrue(m.user.read)
        self.assertTrue(m.user.write)
        self.assertTrue(m.user.execute)

        self.assertTrue(m.group.read)
        self.assertFalse(m.group.write)
        self.assertFalse(m.group.execute)

        self.assertFalse(m.other.read)
        self.assertFalse(m.other.write)
        self.assertFalse(m.other.execute)

    def test_set(self):
        m = opsutils.mode(0640)

        m.group.write = True
        m.other.read = True
        self.assertEqual(m.numeric, 0664)

    def test_set_type(self):
        m = opsutils.mode()

        m.user = 7
        self.assertTrue(m.user.read)
        self.assertTrue(m.user.write)
        self.assertTrue(m.user.execute)

        m.group = 5
        self.assertTrue(m.group.read)
        self.assertFalse(m.group.write)
        self.assertTrue(m.group.execute)

        m.other = 2
        self.assertFalse(m.other.read)
        self.assertTrue(m.other.write)
        self.assertFalse(m.other.execute)

if __name__ == '__main__':
    unittest.main()
