import numbers
import os
import unittest
import opsutils

class EnvGetTestCase(unittest.TestCase):

    def setUp(self):
        os.environ.clear()
        os.environ['opsutils-string'] = 'string'
        os.environ['opsutils-unicode'] = u'unicode'
        os.environ['opsutils-integer'] = '+10'
        os.environ['opsutils-float'] = '-10.5'

    def test_default(self):
        self.assertEqual(opsutils.env.get('opsutils-empty'), '')
        self.assertEqual(opsutils.env.get('opsutils-empty', default='test'), 'test')

        self.assertEqual(opsutils.env.get('opsutils-string'), 'string')
        self.assertEqual(opsutils.env.get('opsutils-string', default='test'), 'string')

        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer'), str))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-string'), str))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-unicode'), unicode))

    def test_string(self):
        self.assertEqual(opsutils.env.get('opsutils-empty', type='string'), '')
        self.assertEqual(opsutils.env.get('opsutils-empty', default='test', type='string'), 'test')

        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type=str), str))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type='str'), str))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type='string'), str))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-unicode', type='string'), str))

    def test_unicode(self):
        self.assertEqual(opsutils.env.get('opsutils-empty', type='unicode'), '')
        self.assertEqual(opsutils.env.get('opsutils-empty', default=u'test', type='unicode'), u'test')

        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type=unicode), unicode))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type='unicode'), unicode))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-string', type='unicode'), unicode))

    def test_boolean(self):
        os.environ['opsutils-boolean-one'] = '1'
        os.environ['opsutils-boolean-zero'] = '0'
        os.environ['opsutils-boolean-true'] = 'true'
        os.environ['opsutils-boolean-false'] = 'false'
        os.environ['opsutils-boolean-yes'] = 'yes'
        os.environ['opsutils-boolean-no'] = 'no'

        self.assertEqual(opsutils.env.get('opsutils-empty', type='boolean'), False)
        self.assertEqual(opsutils.env.get('opsutils-empty', default=True, type='boolean'), True)

        self.assertEqual(opsutils.env.get('opsutils-boolean-zero', type='boolean'), False)
        self.assertEqual(opsutils.env.get('opsutils-boolean-one', type='boolean'), True)
        self.assertEqual(opsutils.env.get('opsutils-boolean-true', type='boolean'), True)
        self.assertEqual(opsutils.env.get('opsutils-boolean-false', type='boolean'), False)
        self.assertEqual(opsutils.env.get('opsutils-boolean-yes', type='boolean'), True)
        self.assertEqual(opsutils.env.get('opsutils-boolean-no', type='boolean'), False)

    def test_number(self):
        self.assertEqual(opsutils.env.get('opsutils-empty', type='number'), 0)
        self.assertEqual(opsutils.env.get('opsutils-empty', default=5, type='number'), 5)

        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type=numbers.Number), int))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type='number'), int))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-float', type='number'), float))

    def test_integer(self):
        os.environ['opsutils-integer-invalid'] = '.'

        self.assertEqual(opsutils.env.get('opsutils-empty', type='integer'), 0)
        self.assertEqual(opsutils.env.get('opsutils-empty', default=5, type='integer'), 5)
        self.assertEqual(opsutils.env.get('opsutils-integer-invalid', default=5, type='integer'), 5)
        self.assertEqual(opsutils.env.get('opsutils-float', type='integer'), -10)

        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type=int), int))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type='int'), int))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-float', type='int'), int))

    def test_float(self):
        os.environ['opsutils-float-invalid'] = '.'

        self.assertEqual(opsutils.env.get('opsutils-empty', type='float'), 0.0)
        self.assertEqual(opsutils.env.get('opsutils-empty', default=5.0, type='float'), 5.0)
        self.assertEqual(opsutils.env.get('opsutils-float-invalid', default=5.0, type='float'), 5.0)
        self.assertEqual(opsutils.env.get('opsutils-integer', type='float'), 10.0)
        self.assertEqual(opsutils.env.get('opsutils-float', type='float'), -10.5)

        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type=float), float))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type='float'), float))
        self.assertTrue(isinstance(opsutils.env.get('opsutils-integer', type='float'), float))

class EnvSetTestCase(unittest.TestCase):

    def setUp(self):
        os.environ.clear()
        os.environ['opsutils'] = 'one'

    def test_add(self):
        opsutils.env.set('opsutils', 'two', add=True)
        self.assertEqual(opsutils.env.get('opsutils'), 'one')

        opsutils.env.set('opsutils-two', 'two', add=True)
        self.assertEqual(opsutils.env.get('opsutils-two'), 'two')

    def test_append(self):
        opsutils.env.set('opsutils', 'two', append=True, sep='')
        self.assertEqual(opsutils.env.get('opsutils'), 'onetwo')

        opsutils.env.set('opsutils', 'three', append=True)
        self.assertEqual(opsutils.env.get('opsutils'), 'onetwo:three')

        self.assertFalse(opsutils.env.set('opsutils', 'onetwo', append=True, unique=True))
        self.assertFalse(opsutils.env.set('opsutils', 'three', append=True, unique=True))
        self.assertTrue(opsutils.env.set('opsutils', 'four', append=True, unique=True))
        self.assertEqual(opsutils.env.get('opsutils'), 'onetwo:three:four')

        self.assertTrue(opsutils.env.set('opsutils-two', 'one', prepend=True, unique=True))
        self.assertEqual(opsutils.env.get('opsutils-two'), 'one')

    def test_prepend(self):
        opsutils.env.set('opsutils', 'two', prepend=True, sep='')
        self.assertEqual(opsutils.env.get('opsutils'), 'twoone')

        opsutils.env.set('opsutils', 'three', prepend=True)
        self.assertEqual(opsutils.env.get('opsutils'), 'three:twoone')

        self.assertFalse(opsutils.env.set('opsutils', 'twoone', prepend=True, unique=True))
        self.assertFalse(opsutils.env.set('opsutils', 'three', prepend=True, unique=True))
        self.assertTrue(opsutils.env.set('opsutils', 'four', prepend=True, unique=True))
        self.assertEqual(opsutils.env.get('opsutils'), 'four:three:twoone')

        self.assertTrue(opsutils.env.set('opsutils-two', 'one', prepend=True, unique=True))
        self.assertEqual(opsutils.env.get('opsutils-two'), 'one')

    def test_set(self):
        opsutils.env.set('opsutils', 'two')
        self.assertEqual(opsutils.env.get('opsutils'), 'two')

if __name__ == '__main__':
    unittest.main()
