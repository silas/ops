import numbers
import os
import unittest
import ops.exceptions
import ops.utils

class EnvGetTestCase(unittest.TestCase):

    def setUp(self):
        os.environ.clear()
        os.environ['ops.utils-string'] = 'string'
        os.environ['ops.utils-unicode'] = u'unicode'
        os.environ['ops.utils-integer'] = '+10'
        os.environ['ops.utils-float'] = '-10.5'
        os.environ['ops.utils-boolean-true'] = 'true'
        os.environ['ops.utils-boolean-false'] = 'false'

    def test_default(self):
        self.assertEqual(ops.utils.env_get('ops.utils-empty'), '')
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default='test'), 'test')

        self.assertEqual(ops.utils.env_get('ops.utils-string'), 'string')
        self.assertEqual(ops.utils.env_get('ops.utils-string', default='test'), 'string')

        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-integer'), str))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-string'), str))
        self.assertTrue(isinstance(ops.utils.env_get('ops.utils-unicode'), unicode))

    def test_string(self):
        TYPE='string'

        self.assertEqual(ops.utils.env_get('ops.utils-empty', type=TYPE), '')
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default='test', type=TYPE), 'test')

        self.assertEqual(ops.utils.env_get('ops.utils-string', type=TYPE), 'string')
        self.assertRaises(ops.exceptions.ValidationError, ops.utils.env_get, 'ops.utils-empty', type=TYPE, raise_exception=True)

    def test_unicode(self):
        TYPE='unicode'

        self.assertEqual(ops.utils.env_get('ops.utils-empty', type=TYPE), '')
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default=u'test', type=TYPE), u'test')

        self.assertEqual(ops.utils.env_get('ops.utils-unicode', type=TYPE), 'unicode')
        self.assertRaises(ops.exceptions.ValidationError, ops.utils.env_get, 'ops.utils-empty', type=TYPE, raise_exception=True)

    def test_boolean(self):
        TYPE='boolean'

        self.assertEqual(ops.utils.env_get('ops.utils-empty', type=TYPE), False)
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default=True, type=TYPE), True)

        self.assertEqual(ops.utils.env_get('ops.utils-boolean-true', type=TYPE), True)
        self.assertEqual(ops.utils.env_get('ops.utils-boolean-false', type=TYPE), False)
        self.assertRaises(ops.exceptions.ValidationError, ops.utils.env_get, 'ops.utils-string', type=TYPE, raise_exception=True)

    def test_number(self):
        TYPE='number'

        self.assertEqual(ops.utils.env_get('ops.utils-empty', type=TYPE), 0)
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default=5, type=TYPE), 5)

        self.assertEqual(ops.utils.env_get('ops.utils-integer', type=TYPE), 10)
        self.assertEqual(ops.utils.env_get('ops.utils-float', type=TYPE), -10.5)
        self.assertRaises(ops.exceptions.ValidationError, ops.utils.env_get, 'ops.utils-string', type=TYPE, raise_exception=True)

    def test_integer(self):
        TYPE='integer'

        self.assertEqual(ops.utils.env_get('ops.utils-empty', type=TYPE), 0)
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default=5, type=TYPE), 5)
        self.assertEqual(ops.utils.env_get('ops.utils-integer', type=TYPE), 10)
        self.assertEqual(ops.utils.env_get('ops.utils-float', type=TYPE), -10)

        self.assertRaises(ops.exceptions.ValidationError, ops.utils.env_get, 'ops.utils-string', type=TYPE, raise_exception=True)

    def test_float(self):
        TYPE='float'

        self.assertEqual(ops.utils.env_get('ops.utils-empty', type=TYPE), 0.0)
        self.assertEqual(ops.utils.env_get('ops.utils-empty', default=5.0, type=TYPE), 5.0)
        self.assertEqual(ops.utils.env_get('ops.utils-integer', type=TYPE), 10.0)
        self.assertEqual(ops.utils.env_get('ops.utils-float', type=TYPE), -10.5)

        self.assertRaises(ops.exceptions.ValidationError, ops.utils.env_get, 'ops.utils-string', type=TYPE, raise_exception=True)

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
