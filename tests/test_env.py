import numbers
import os
import unittest
import ops

class EnvGetTestCase(unittest.TestCase):

    def setUp(self):
        os.environ.clear()
        os.environ['ops-string'] = 'string'
        os.environ['ops-unicode'] = u'unicode'
        os.environ['ops-integer'] = '+10'
        os.environ['ops-float'] = '-10.5'
        os.environ['ops-boolean-true'] = 'true'
        os.environ['ops-boolean-false'] = 'false'

    def test_default(self):
        self.assertEqual(ops.env.get('ops-empty'), '')
        self.assertEqual(ops.env.get('ops-empty', default='test'), 'test')

        self.assertEqual(ops.env.get('ops-string'), 'string')
        self.assertEqual(ops.env.get('ops-string', default='test'), 'string')

        self.assertTrue(isinstance(ops.env.get('ops-integer'), str))
        self.assertTrue(isinstance(ops.env.get('ops-string'), str))
        self.assertTrue(isinstance(ops.env.get('ops-unicode'), unicode))

    def test_string(self):
        TYPE='string'

        self.assertEqual(ops.env.get('ops-empty', type=TYPE), '')
        self.assertEqual(ops.env.get('ops-empty', default='test', type=TYPE), 'test')

        self.assertEqual(ops.env.get('ops-string', type=TYPE), 'string')
        self.assertRaises(ops.ValidationError, ops.env.get, 'ops-empty', type=TYPE, raise_exception=True)

    def test_unicode(self):
        TYPE='unicode'

        self.assertEqual(ops.env.get('ops-empty', type=TYPE), '')
        self.assertEqual(ops.env.get('ops-empty', default=u'test', type=TYPE), u'test')

        self.assertEqual(ops.env.get('ops-unicode', type=TYPE), 'unicode')
        self.assertRaises(ops.ValidationError, ops.env.get, 'ops-empty', type=TYPE, raise_exception=True)

    def test_boolean(self):
        TYPE='boolean'

        self.assertEqual(ops.env.get('ops-empty', type=TYPE), False)
        self.assertEqual(ops.env.get('ops-empty', default=True, type=TYPE), True)

        self.assertEqual(ops.env.get('ops-boolean-true', type=TYPE), True)
        self.assertEqual(ops.env.get('ops-boolean-false', type=TYPE), False)
        self.assertRaises(ops.ValidationError, ops.env.get, 'ops-string', type=TYPE, raise_exception=True)

    def test_number(self):
        TYPE='number'

        self.assertEqual(ops.env.get('ops-empty', type=TYPE), 0)
        self.assertEqual(ops.env.get('ops-empty', default=5, type=TYPE), 5)

        self.assertEqual(ops.env.get('ops-integer', type=TYPE), 10)
        self.assertEqual(ops.env.get('ops-float', type=TYPE), -10.5)
        self.assertRaises(ops.ValidationError, ops.env.get, 'ops-string', type=TYPE, raise_exception=True)

    def test_integer(self):
        TYPE='integer'

        self.assertEqual(ops.env.get('ops-empty', type=TYPE), 0)
        self.assertEqual(ops.env.get('ops-empty', default=5, type=TYPE), 5)
        self.assertEqual(ops.env.get('ops-integer', type=TYPE), 10)
        self.assertEqual(ops.env.get('ops-float', type=TYPE), -10)

        self.assertRaises(ops.ValidationError, ops.env.get, 'ops-string', type=TYPE, raise_exception=True)

    def test_float(self):
        TYPE='float'

        self.assertEqual(ops.env.get('ops-empty', type=TYPE), 0.0)
        self.assertEqual(ops.env.get('ops-empty', default=5.0, type=TYPE), 5.0)
        self.assertEqual(ops.env.get('ops-integer', type=TYPE), 10.0)
        self.assertEqual(ops.env.get('ops-float', type=TYPE), -10.5)

        self.assertRaises(ops.ValidationError, ops.env.get, 'ops-string', type=TYPE, raise_exception=True)

class EnvSetTestCase(unittest.TestCase):

    def setUp(self):
        os.environ.clear()
        os.environ['ops'] = 'one'

    def test_add(self):
        ops.env.set('ops', 'two', add=True)
        self.assertEqual(ops.env.get('ops'), 'one')

        ops.env.set('ops-two', 'two', add=True)
        self.assertEqual(ops.env.get('ops-two'), 'two')

    def test_call(self):
        ops.env('ops', 'call')
        self.assertEqual(ops.env('ops'), 'call')

    def test_append(self):
        ops.env.set('ops', 'two', append=True, sep='')
        self.assertEqual(ops.env.get('ops'), 'onetwo')

        ops.env.set('ops', 'three', append=True)
        self.assertEqual(ops.env.get('ops'), 'onetwo:three')

        self.assertFalse(ops.env.set('ops', 'onetwo', append=True, unique=True))
        self.assertFalse(ops.env.set('ops', 'three', append=True, unique=True))
        self.assertTrue(ops.env.set('ops', 'four', append=True, unique=True))
        self.assertEqual(ops.env.get('ops'), 'onetwo:three:four')

        self.assertTrue(ops.env.set('ops-two', 'one', prepend=True, unique=True))
        self.assertEqual(ops.env.get('ops-two'), 'one')

    def test_prepend(self):
        ops.env.set('ops', 'two', prepend=True, sep='')
        self.assertEqual(ops.env.get('ops'), 'twoone')

        ops.env.set('ops', 'three', prepend=True)
        self.assertEqual(ops.env.get('ops'), 'three:twoone')

        self.assertFalse(ops.env.set('ops', 'twoone', prepend=True, unique=True))
        self.assertFalse(ops.env.set('ops', 'three', prepend=True, unique=True))
        self.assertTrue(ops.env.set('ops', 'four', prepend=True, unique=True))
        self.assertEqual(ops.env.get('ops'), 'four:three:twoone')

        self.assertTrue(ops.env.set('ops-two', 'one', prepend=True, unique=True))
        self.assertEqual(ops.env.get('ops-two'), 'one')

    def test_set(self):
        ops.env.set('ops', 'two')
        self.assertEqual(ops.env.get('ops'), 'two')

if __name__ == '__main__':
    unittest.main()
