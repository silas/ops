import numbers
import os
import unittest
import ops.utils

class EnvGetTestCase(unittest.TestCase):

    def setUp(self):
        os.environ.clear()
        os.environ['ops.utils-string'] = 'string'
        os.environ['ops.utils-unicode'] = u'unicode'
        os.environ['ops.utils-integer'] = '+10'
        os.environ['ops.utils-float'] = '-10.5'

    def test_default(self):
        self.assertEqual(ops.utils.env_get('ops.utils-empty'), '')
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default='test'), 'test')

        self.assertEqual(ops.utils.env_get('ops.utils-string'), 'string')
        self.assertEqual(ops.utils.env_get('ops.utils-string', default='test'), 'string')

        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer'), str))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-string'), str))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-unicode'), unicode))

    def test_string(self):
        self.assertEqual(ops.utils.env_get('ops.utils-empty', type='string'), '')
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default='test', type='string'), 'test')

        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type=str), str))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type='str'), str))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type='string'), str))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-unicode', type='string'), str))

    def test_unicode(self):
        self.assertEqual(ops.utils.env_get('ops.utils-empty', type='unicode'), '')
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default=u'test', type='unicode'), u'test')

        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type=unicode), unicode))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type='unicode'), unicode))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-string', type='unicode'), unicode))

    def test_boolean(self):
        os.environ['ops.utils-boolean-one'] = '1'
        os.environ['ops.utils-boolean-zero'] = '0'
        os.environ['ops.utils-boolean-true'] = 'true'
        os.environ['ops.utils-boolean-false'] = 'false'
        os.environ['ops.utils-boolean-yes'] = 'yes'
        os.environ['ops.utils-boolean-no'] = 'no'

        self.assertEqual(ops.utils.env_get('ops.utils-empty', type='boolean'), False)
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default=True, type='boolean'), True)

        self.assertEqual(ops.utils.env_get('ops.utils-boolean-zero', type='boolean'), False)
        self.assertEqual(ops.utils.env_get('ops.utils-boolean-one', type='boolean'), True)
        self.assertEqual(ops.utils.env_get('ops.utils-boolean-true', type='boolean'), True)
        self.assertEqual(ops.utils.env_get('ops.utils-boolean-false', type='boolean'), False)
        self.assertEqual(ops.utils.env_get('ops.utils-boolean-yes', type='boolean'), True)
        self.assertEqual(ops.utils.env_get('ops.utils-boolean-no', type='boolean'), False)

    def test_number(self):
        self.assertEqual(ops.utils.env_get('ops.utils-empty', type='number'), 0)
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default=5, type='number'), 5)

        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type=numbers.Number), int))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type='number'), int))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-float', type='number'), float))

    def test_integer(self):
        os.environ['ops.utils-integer-invalid'] = '.'

        self.assertEqual(ops.utils.env_get('ops.utils-empty', type='integer'), 0)
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default=5, type='integer'), 5)
        self.assertEqual(ops.utils.env_get('ops.utils-integer-invalid', default=5, type='integer'), 5)
        self.assertEqual(ops.utils.env_get('ops.utils-float', type='integer'), -10)

        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type=int), int))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type='int'), int))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-float', type='int'), int))

    def test_float(self):
        os.environ['ops.utils-float-invalid'] = '.'

        self.assertEqual(ops.utils.env_get('ops.utils-empty', type='float'), 0.0)
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default=5.0, type='float'), 5.0)
        self.assertEqual(ops.utils.env_get('ops.utils-float-invalid', default=5.0, type='float'), 5.0)
        self.assertEqual(ops.utils.env_get('ops.utils-integer', type='float'), 10.0)
        self.assertEqual(ops.utils.env_get('ops.utils-float', type='float'), -10.5)

        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type=float), float))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type='float'), float))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer', type='float'), float))

class EnvSetTestCase(unittest.TestCase):

    def setUp(self):
        os.environ.clear()
        os.environ['ops.utils'] = 'one'

    def test_add(self):
        ops.utils.env_set('ops.utils', 'two', add=True)
        self.assertEqual(ops.utils.env_get('ops.utils'), 'one')

        ops.utils.env_set('ops.utils-two', 'two', add=True)
        self.assertEqual(ops.utils.env_get('ops.utils-two'), 'two')

    def test_append(self):
        ops.utils.env_set('ops.utils', 'two', append=True, sep='')
        self.assertEqual(ops.utils.env_get('ops.utils'), 'onetwo')

        ops.utils.env_set('ops.utils', 'three', append=True)
        self.assertEqual(ops.utils.env_get('ops.utils'), 'onetwo:three')

        self.assertFalse(ops.utils.env_set('ops.utils', 'onetwo', append=True, unique=True))
        self.assertFalse(ops.utils.env_set('ops.utils', 'three', append=True, unique=True))
        self.assertTrue(ops.utils.env_set('ops.utils', 'four', append=True, unique=True))
        self.assertEqual(ops.utils.env_get('ops.utils'), 'onetwo:three:four')

        self.assertTrue(ops.utils.env_set('ops.utils-two', 'one', prepend=True, unique=True))
        self.assertEqual(ops.utils.env_get('ops.utils-two'), 'one')

    def test_prepend(self):
        ops.utils.env_set('ops.utils', 'two', prepend=True, sep='')
        self.assertEqual(ops.utils.env_get('ops.utils'), 'twoone')

        ops.utils.env_set('ops.utils', 'three', prepend=True)
        self.assertEqual(ops.utils.env_get('ops.utils'), 'three:twoone')

        self.assertFalse(ops.utils.env_set('ops.utils', 'twoone', prepend=True, unique=True))
        self.assertFalse(ops.utils.env_set('ops.utils', 'three', prepend=True, unique=True))
        self.assertTrue(ops.utils.env_set('ops.utils', 'four', prepend=True, unique=True))
        self.assertEqual(ops.utils.env_get('ops.utils'), 'four:three:twoone')

        self.assertTrue(ops.utils.env_set('ops.utils-two', 'one', prepend=True, unique=True))
        self.assertEqual(ops.utils.env_get('ops.utils-two'), 'one')

    def test_set(self):
        ops.utils.env_set('ops.utils', 'two')
        self.assertEqual(ops.utils.env_get('ops.utils'), 'two')

if __name__ == '__main__':
    unittest.main()
