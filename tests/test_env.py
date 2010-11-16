import numbers
import os
import unittest
import opsutils

class GetEnvTestCase(unittest.TestCase):

    def setUp(self):
        os.environ.clear()
        os.environ['opsutils-string'] = 'string'
        os.environ['opsutils-unicode'] = u'unicode'
        os.environ['opsutils-integer'] = '+10'
        os.environ['opsutils-float'] = '-10.5'

    def test_default(self):
        self.assertEqual(opsutils.getenv('opsutils-empty'), '')
        self.assertEqual(opsutils.getenv('opsutils-empty', default='test'), 'test')

        self.assertEqual(opsutils.getenv('opsutils-string'), 'string')
        self.assertEqual(opsutils.getenv('opsutils-string', default='test'), 'string')

        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer'), str))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-string'), str))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-unicode'), unicode))

    def test_string(self):
        self.assertEqual(opsutils.getenv('opsutils-empty', type='string'), '')
        self.assertEqual(opsutils.getenv('opsutils-empty', default='test', type='string'), 'test')

        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type=str), str))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type='str'), str))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type='string'), str))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-unicode', type='string'), str))

    def test_unicode(self):
        self.assertEqual(opsutils.getenv('opsutils-empty', type='unicode'), '')
        self.assertEqual(opsutils.getenv('opsutils-empty', default=u'test', type='unicode'), u'test')

        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type=unicode), unicode))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type='unicode'), unicode))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-string', type='unicode'), unicode))

    def test_boolean(self):
        os.environ['opsutils-boolean-one'] = '1'
        os.environ['opsutils-boolean-zero'] = '0'
        os.environ['opsutils-boolean-true'] = 'true'
        os.environ['opsutils-boolean-false'] = 'false'
        os.environ['opsutils-boolean-yes'] = 'yes'
        os.environ['opsutils-boolean-no'] = 'no'

        self.assertEqual(opsutils.getenv('opsutils-empty', type='boolean'), False)
        self.assertEqual(opsutils.getenv('opsutils-empty', default=True, type='boolean'), True)

        self.assertEqual(opsutils.getenv('opsutils-boolean-zero', type='boolean'), False)
        self.assertEqual(opsutils.getenv('opsutils-boolean-one', type='boolean'), True)
        self.assertEqual(opsutils.getenv('opsutils-boolean-true', type='boolean'), True)
        self.assertEqual(opsutils.getenv('opsutils-boolean-false', type='boolean'), False)
        self.assertEqual(opsutils.getenv('opsutils-boolean-yes', type='boolean'), True)
        self.assertEqual(opsutils.getenv('opsutils-boolean-no', type='boolean'), False)

    def test_number(self):
        self.assertEqual(opsutils.getenv('opsutils-empty', type='number'), 0)
        self.assertEqual(opsutils.getenv('opsutils-empty', default=5, type='number'), 5)

        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type=numbers.Number), int))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type='number'), int))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-float', type='number'), float))

    def test_integer(self):
        os.environ['opsutils-integer-invalid'] = '.'

        self.assertEqual(opsutils.getenv('opsutils-empty', type='integer'), 0)
        self.assertEqual(opsutils.getenv('opsutils-empty', default=5, type='integer'), 5)
        self.assertEqual(opsutils.getenv('opsutils-integer-invalid', default=5, type='integer'), 5)
        self.assertEqual(opsutils.getenv('opsutils-float', type='integer'), -10)

        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type=int), int))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type='int'), int))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-float', type='int'), int))

    def test_float(self):
        os.environ['opsutils-float-invalid'] = '.'

        self.assertEqual(opsutils.getenv('opsutils-empty', type='float'), 0.0)
        self.assertEqual(opsutils.getenv('opsutils-empty', default=5.0, type='float'), 5.0)
        self.assertEqual(opsutils.getenv('opsutils-float-invalid', default=5.0, type='float'), 5.0)
        self.assertEqual(opsutils.getenv('opsutils-integer', type='float'), 10.0)
        self.assertEqual(opsutils.getenv('opsutils-float', type='float'), -10.5)

        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type=float), float))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type='float'), float))
        self.assertTrue(isinstance(opsutils.getenv('opsutils-integer', type='float'), float))

class SetEnvTestCase(unittest.TestCase):

    def setUp(self):
        os.environ.clear()
        os.environ['opsutils'] = 'one'

    def test_add(self):
        opsutils.setenv('opsutils', 'two', add=True)
        self.assertEqual(opsutils.getenv('opsutils'), 'one')

        opsutils.setenv('opsutils-two', 'two', add=True)
        self.assertEqual(opsutils.getenv('opsutils-two'), 'two')

    def test_append(self):
        opsutils.setenv('opsutils', 'two', append=True, sep='')
        self.assertEqual(opsutils.getenv('opsutils'), 'onetwo')

        opsutils.setenv('opsutils', 'three', append=True)
        self.assertEqual(opsutils.getenv('opsutils'), 'onetwo:three')

        self.assertFalse(opsutils.setenv('opsutils', 'onetwo', append=True, unique=True))
        self.assertFalse(opsutils.setenv('opsutils', 'three', append=True, unique=True))
        self.assertTrue(opsutils.setenv('opsutils', 'four', append=True, unique=True))
        self.assertEqual(opsutils.getenv('opsutils'), 'onetwo:three:four')

        self.assertTrue(opsutils.setenv('opsutils-two', 'one', prepend=True, unique=True))
        self.assertEqual(opsutils.getenv('opsutils-two'), 'one')

    def test_prepend(self):
        opsutils.setenv('opsutils', 'two', prepend=True, sep='')
        self.assertEqual(opsutils.getenv('opsutils'), 'twoone')

        opsutils.setenv('opsutils', 'three', prepend=True)
        self.assertEqual(opsutils.getenv('opsutils'), 'three:twoone')

        self.assertFalse(opsutils.setenv('opsutils', 'twoone', prepend=True, unique=True))
        self.assertFalse(opsutils.setenv('opsutils', 'three', prepend=True, unique=True))
        self.assertTrue(opsutils.setenv('opsutils', 'four', prepend=True, unique=True))
        self.assertEqual(opsutils.getenv('opsutils'), 'four:three:twoone')

        self.assertTrue(opsutils.setenv('opsutils-two', 'one', prepend=True, unique=True))
        self.assertEqual(opsutils.getenv('opsutils-two'), 'one')

    def test_set(self):
        opsutils.setenv('opsutils', 'two')
        self.assertEqual(opsutils.getenv('opsutils'), 'two')

if __name__ == '__main__':
    unittest.main()
