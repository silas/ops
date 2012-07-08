import numbers
import os
import unittest
import ops

class EnvGetTestCase(unittest.TestCase):

    def setUp(self):
        environ = {}
        environ['ops-string'] = 'string'
        environ['ops-unicode'] = u'unicode'
        environ['ops-integer'] = '+10'
        environ['ops-float'] = '-10.5'
        environ['ops-boolean-true'] = 'true'
        environ['ops-boolean-false'] = 'false'
        self.env = ops.Env(environ)

    def test_default(self):
        self.assertEqual(self.env.get('ops-empty'), '')
        self.assertEqual(self.env.get('ops-empty', default='test'), 'test')

        self.assertEqual(self.env.get('ops-string'), 'string')
        self.assertEqual(self.env.get('ops-string', default='test'), 'string')

        self.assertTrue(isinstance(self.env.get('ops-integer'), str))
        self.assertTrue(isinstance(self.env.get('ops-string'), str))
        self.assertTrue(isinstance(self.env.get('ops-unicode'), unicode))

    def test_string(self):
        TYPE='string'

        self.assertEqual(self.env.get('ops-empty', type=TYPE), '')
        self.assertEqual(self.env.get('ops-empty', default='test', type=TYPE), 'test')

        self.assertEqual(self.env.get('ops-string', type=TYPE), 'string')
        self.assertRaises(ops.ValidationError, self.env.get, 'ops-empty', type=TYPE, raise_exception=True)

    def test_unicode(self):
        TYPE='unicode'

        self.assertEqual(self.env.get('ops-empty', type=TYPE), '')
        self.assertEqual(self.env.get('ops-empty', default=u'test', type=TYPE), u'test')

        self.assertEqual(self.env.get('ops-unicode', type=TYPE), 'unicode')
        self.assertRaises(ops.ValidationError, self.env.get, 'ops-empty', type=TYPE, raise_exception=True)

    def test_boolean(self):
        TYPE='boolean'

        self.assertEqual(self.env.get('ops-empty', type=TYPE), False)
        self.assertEqual(self.env.get('ops-empty', default=True, type=TYPE), True)

        self.assertEqual(self.env.get('ops-boolean-true', type=TYPE), True)
        self.assertEqual(self.env.get('ops-boolean-false', type=TYPE), False)
        self.assertRaises(ops.ValidationError, self.env.get, 'ops-string', type=TYPE, raise_exception=True)

    def test_number(self):
        TYPE='number'

        self.assertEqual(self.env.get('ops-empty', type=TYPE), 0)
        self.assertEqual(self.env.get('ops-empty', default=5, type=TYPE), 5)

        self.assertEqual(self.env.get('ops-integer', type=TYPE), 10)
        self.assertEqual(self.env.get('ops-float', type=TYPE), -10.5)
        self.assertRaises(ops.ValidationError, self.env.get, 'ops-string', type=TYPE, raise_exception=True)

    def test_integer(self):
        TYPE='integer'

        self.assertEqual(self.env.get('ops-empty', type=TYPE), 0)
        self.assertEqual(self.env.get('ops-empty', default=5, type=TYPE), 5)
        self.assertEqual(self.env.get('ops-integer', type=TYPE), 10)
        self.assertEqual(self.env.get('ops-float', type=TYPE), -10)

        self.assertRaises(ops.ValidationError, self.env.get, 'ops-string', type=TYPE, raise_exception=True)

    def test_float(self):
        TYPE='float'

        self.assertEqual(self.env.get('ops-empty', type=TYPE), 0.0)
        self.assertEqual(self.env.get('ops-empty', default=5.0, type=TYPE), 5.0)
        self.assertEqual(self.env.get('ops-integer', type=TYPE), 10.0)
        self.assertEqual(self.env.get('ops-float', type=TYPE), -10.5)

        self.assertRaises(ops.ValidationError, self.env.get, 'ops-string', type=TYPE, raise_exception=True)

class EnvSetTestCase(unittest.TestCase):

    def setUp(self):
        self.environ = {}
        self.environ['ops'] = 'one'
        self.env = ops.Env(self.environ)

    def test_add(self):
        self.env.set('ops', 'two', add=True)
        self.assertEqual(self.env.get('ops'), 'one')

        self.env.set('ops-two', 'two', add=True)
        self.assertEqual(self.env.get('ops-two'), 'two')

    def test_call(self):
        data = self.env()
        self.assertEqual(len(data), len(self.environ))
        self.assertEqual(data['ops'], self.environ['ops'])

        self.env('ops', 'call')
        self.assertEqual(self.env('ops'), 'call')

    def test_append(self):
        self.env.set('ops', 'two', append=True, sep='')
        self.assertEqual(self.env.get('ops'), 'onetwo')

        self.env.set('ops', 'three', append=True)
        self.assertEqual(self.env.get('ops'), 'onetwo:three')

        self.assertFalse(self.env.set('ops', 'onetwo', append=True, unique=True))
        self.assertFalse(self.env.set('ops', 'three', append=True, unique=True))
        self.assertTrue(self.env.set('ops', 'four', append=True, unique=True))
        self.assertEqual(self.env.get('ops'), 'onetwo:three:four')

        self.assertTrue(self.env.set('ops-two', 'one', prepend=True, unique=True))
        self.assertEqual(self.env.get('ops-two'), 'one')

    def test_prepend(self):
        self.env.set('ops', 'two', prepend=True, sep='')
        self.assertEqual(self.env.get('ops'), 'twoone')

        self.env.set('ops', 'three', prepend=True)
        self.assertEqual(self.env.get('ops'), 'three:twoone')

        self.assertFalse(self.env.set('ops', 'twoone', prepend=True, unique=True))
        self.assertFalse(self.env.set('ops', 'three', prepend=True, unique=True))
        self.assertTrue(self.env.set('ops', 'four', prepend=True, unique=True))
        self.assertEqual(self.env.get('ops'), 'four:three:twoone')

        self.assertTrue(self.env.set('ops-two', 'one', prepend=True, unique=True))
        self.assertEqual(self.env.get('ops-two'), 'one')

    def test_del(self):
        del self.env['ops']
        self.assertEqual(self.env.get('ops'), '')

    def test_get(self):
        self.assertEqual(self.env['ops'], 'one')
        self.assertEqual(self.env.get('ops'), 'one')

    def test_set(self):
        self.env.set('ops', 'two')
        self.assertEqual(self.env.get('ops'), 'two')
        self.env['ops'] = 'three'
        self.assertEqual(self.env.get('ops'), 'three')
        self.env.set('ops', True)
        self.assertEqual(self.env.get('ops'), 'True')
        self.env.set('ops', True, append=True, sep=1)
        self.assertEqual(self.env.get('ops'), 'True1True')

    def test_iter(self):
        self.assertEqual(list(self.env)[0], 'ops')

if __name__ == '__main__':
    unittest.main()
