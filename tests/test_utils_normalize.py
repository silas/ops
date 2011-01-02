import numbers
import os
import unittest
import ops.exceptions
import ops.utils

class NormalizeTestCase(unittest.TestCase):

    def assertNormalizes(self, src, dst, ntype):
        value = ops.utils.normalize(src, type=ntype)
        self.assertTrue(isinstance(value, type(dst)))
        self.assertEqual(value, dst)

    def assertNormalizesRaises(self, value, ntype):
        self.assertRaises(ops.exceptions.ValidationError, ops.utils.normalize, value, type=ntype, raise_exception=True)

    def test_string(self):
        TYPE = 'string'

        self.assertNormalizes(u'abc', 'abc', str)
        self.assertNormalizes(u'abc', 'abc', 'str')
        self.assertNormalizes(u'abc', 'abc', 'string')

        self.assertNormalizes(u'', '', TYPE)

        self.assertNormalizes(123, '123', TYPE)
        self.assertNormalizes(1.0, '1.0', TYPE)

    def test_unicode(self):
        TYPE = 'unicode'

        self.assertNormalizes('abc', u'abc', unicode)
        self.assertNormalizes('abc', u'abc', 'unicode')

        self.assertNormalizes('', u'', TYPE)

        self.assertNormalizes(123, u'123', TYPE)
        self.assertNormalizes(1.0, u'1.0', TYPE)

    def test_boolean(self):
        TYPE = 'boolean'

        self.assertNormalizes('true', True, bool)
        self.assertNormalizes('true', True, 'bool')
        self.assertNormalizes('true', True, 'boolean')

        self.assertNormalizes('', False, TYPE)

        self.assertNormalizes('1', True, TYPE)
        self.assertNormalizes('0', False, TYPE)
        self.assertNormalizes('true', True, TYPE)
        self.assertNormalizes('false', False, TYPE)
        self.assertNormalizes('yes', True, TYPE)
        self.assertNormalizes('no', False, TYPE)
        self.assertNormalizes('on', True, TYPE)
        self.assertNormalizes('off', False, TYPE)

        self.assertNormalizesRaises('', TYPE)
        self.assertNormalizesRaises('yes, please turn it on', TYPE)

    def test_number(self):
        TYPE = 'number'

        self.assertNormalizes('10', 10, 'number')
        self.assertNormalizes('10', 10, numbers.Number)

        self.assertNormalizes('', 0, TYPE)

        self.assertNormalizes('10', 10, TYPE)
        self.assertNormalizes('+10', 10, TYPE)
        self.assertNormalizes('-10', -10, TYPE)
        self.assertNormalizes('10.5', 10.5, TYPE)
        self.assertNormalizes('+10.5', 10.5, TYPE)
        self.assertNormalizes('-10.5', -10.5, TYPE)
        self.assertNormalizes('1.', 1.0, TYPE)
        self.assertNormalizes('+1.', 1.0, TYPE)
        self.assertNormalizes('-1.', -1.0, TYPE)
        self.assertNormalizes('.5', 0.5, TYPE)
        self.assertNormalizes('+.5', 0.5, TYPE)
        self.assertNormalizes('-.5', -0.5, TYPE)

        self.assertNormalizesRaises('', TYPE)
        self.assertNormalizesRaises('.', TYPE)
        self.assertNormalizesRaises('10i', TYPE)

    def test_integer(self):
        TYPE = 'integer'

        self.assertNormalizes('10', 10, 'int')
        self.assertNormalizes('10', 10, 'integer')
        self.assertNormalizes('10', 10, int)

        self.assertNormalizes('', 0, TYPE)

        self.assertNormalizes('10', 10, TYPE)
        self.assertNormalizes('+10', 10, TYPE)
        self.assertNormalizes('-10', -10, TYPE)
        self.assertNormalizes('10.5', 10, TYPE)
        self.assertNormalizes('+10.5', 10, TYPE)
        self.assertNormalizes('-10.5', -10, TYPE)
        self.assertNormalizes('1.', 1, TYPE)
        self.assertNormalizes('+1.', 1, TYPE)
        self.assertNormalizes('-1.', -1, TYPE)
        self.assertNormalizes('.5', 0, TYPE)
        self.assertNormalizes('+.5', 0, TYPE)
        self.assertNormalizes('-.5', 0, TYPE)

        self.assertNormalizesRaises('', TYPE)
        self.assertNormalizesRaises('.', TYPE)
        self.assertNormalizesRaises('10i', TYPE)

    def test_float(self):
        TYPE = 'float'

        self.assertNormalizes('10.5', 10.5, 'float')
        self.assertNormalizes('10.5', 10.5, float)

        self.assertNormalizes('', 0.0, TYPE)

        self.assertNormalizes('10', 10.0, TYPE)
        self.assertNormalizes('+10', 10.0, TYPE)
        self.assertNormalizes('-10', -10.0, TYPE)
        self.assertNormalizes('10.5', 10.5, TYPE)
        self.assertNormalizes('+10.5', 10.5, TYPE)
        self.assertNormalizes('-10.5', -10.5, TYPE)
        self.assertNormalizes('1.', 1.0, TYPE)
        self.assertNormalizes('+1.', 1.0, TYPE)
        self.assertNormalizes('-1.', -1.0, TYPE)
        self.assertNormalizes('.5', 0.5, TYPE)
        self.assertNormalizes('+.5', 0.5, TYPE)
        self.assertNormalizes('-.5', -0.5, TYPE)

        self.assertNormalizesRaises('', TYPE)
        self.assertNormalizesRaises('.', TYPE)
        self.assertNormalizesRaises('10i', TYPE)

if __name__ == '__main__':
    unittest.main()
