import os
import unittest
import ops.exceptions
import ops.settings

class Settings(ops.settings.Settings):

    class Section(ops.settings.Section):
        boolean_false = ops.settings.Boolean(default=False)
        boolean_true = ops.settings.Boolean(default=True)
        float = ops.settings.Float(default=1.5, min_value=-20, max_value=20)
        integer = ops.settings.Integer(default=1, min_value=-20, max_value=20)
        string = ops.settings.String(default='string', min_length=2, max_length=15)
        number_float = ops.settings.Number(default=2.0, min_value=-20, max_value=20)
        number_integer = ops.settings.Number(default=3, min_value=-20, max_value=20)

class SettingsTestCase(unittest.TestCase):

    _env = {
        'APP_SECTION_BOOLEAN_FALSE': 'true',
        'APP_SECTION_BOOLEAN_TRUE': 'false',
        'APP_SECTION_FLOAT': '+10.5',
        'APP_SECTION_INTEGER': '-10',
        'APP_SECTION_NUMBER_FLOAT': '-6.5',
        'APP_SECTION_NUMBER_INTEGER': '-6',
        'APP_SECTION_STRING': 'env.string',
    }

    def setUp(self):
        os.environ.clear()
        self.name = 'app'

    def setup_boolean(self, value):
        os.environ['APP_SECTION_BOOLEAN_FALSE'] = str(value)

    def setup_float(self, value):
        os.environ['APP_SECTION_FLOAT'] = str(value)

    def setup_integer(self, value):
        os.environ['APP_SECTION_INTEGER'] = str(value)

    def setup_number(self, value):
        os.environ['APP_SECTION_NUMBER_INTEGER'] = str(value)

    def setup_string(self, value):
        os.environ['APP_SECTION_STRING'] = str(value)

    def setup_env(self):
        for name, value in self._env.items():
            os.environ[name] = value

    def setup_configparser(self):
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, 'assets', 'test.cfg')
        return self.parse(config_file=path)

    def parse(self, *args, **kwargs):
        return Settings(name=self.name).parse(*args, **kwargs)

    def test_args(self):
        o = self.parse()
        self.assertFalse(o.args)
        o = self.parse(['one', '--section-boolean-true', 'two'])
        self.assertEqual(len(o.args), 2)
        self.assertEqual(o.args[0], 'one')
        self.assertEqual(o.args[1], 'two')

    def test_boolean_default(self):
        o = self.parse()
        self.assertEqual(o.section.boolean_false, False)
        self.assertEqual(o.section.boolean_true, True)

    def test_boolean_optparse(self):
        o = self.parse(['--section-boolean-false', '--section-boolean-true'])
        self.assertEqual(o.section.boolean_false, True)
        self.assertEqual(o.section.boolean_true, False)

    def test_boolean_configparser(self):
        o = self.setup_configparser()
        self.assertEqual(o.section.boolean_false, True)
        self.assertEqual(o.section.boolean_true, False)

    def test_boolean_env(self):
        self.setup_env()
        o = self.parse()
        self.assertEqual(o.section.boolean_false, True)
        self.assertEqual(o.section.boolean_true, False)

    def test_boolean_exceptions(self):
        self.setup_boolean('test')
        self.assertRaises(ops.exceptions.ValidationError, self.parse)

    def test_float_default(self):
        o = self.parse()
        self.assertEqual(o.section.float, 1.5)

    def test_float_optparse(self):
        o = self.parse(['--section-float', '+11.5'])
        self.assertEqual(o.section.float, 11.5)

    def test_float_configparser(self):
        o = self.setup_configparser()
        self.assertEqual(o.section.float, 12.5)

    def test_float_env(self):
        self.setup_env()
        o = self.parse()
        self.assertEqual(o.section.float, 10.5)

    def test_float_exceptions(self):
        self.setup_float('test')
        self.assertRaises(ops.exceptions.ValidationError, self.parse)
        # Minimum value
        self.setup_float(21)
        self.assertRaises(ops.exceptions.ValidationError, self.parse)
        # Maximum value
        self.setup_float(-21)
        self.assertRaises(ops.exceptions.ValidationError, self.parse)

    def test_integer_default(self):
        o = self.parse()
        self.assertEqual(o.section.integer, 1)

    def test_integer_optparse(self):
        o = self.parse(['--section-integer', '+11.5'])
        self.assertEqual(o.section.integer, 11)

    def test_integer_configparser(self):
        o = self.setup_configparser()
        self.assertEqual(o.section.integer, -12)

    def test_integer_env(self):
        self.setup_env()
        o = self.parse()
        self.assertEqual(o.section.integer, -10)

    def test_integer_exceptions(self):
        self.setup_integer('test')
        self.assertRaises(ops.exceptions.ValidationError, self.parse)
        # Minimum value
        self.setup_integer(21)
        self.assertRaises(ops.exceptions.ValidationError, self.parse)
        # Maximum value
        self.setup_integer(-21)
        self.assertRaises(ops.exceptions.ValidationError, self.parse)

    def test_number_default(self):
        o = self.parse()
        self.assertEqual(o.section.number_float, 2.0)
        self.assertTrue(isinstance(o.section.number_float, float))
        self.assertEqual(o.section.number_integer, 3)
        self.assertTrue(isinstance(o.section.number_integer, int))

    def test_number_optparse(self):
        o = self.parse(['--section-number-float', '-11.5', '--section-number-integer', '+11'])
        self.assertEqual(o.section.number_float, -11.5)
        self.assertTrue(isinstance(o.section.number_float, float))
        self.assertEqual(o.section.number_integer, 11)
        self.assertTrue(isinstance(o.section.number_integer, int))

    def test_number_configparser(self):
        o = self.setup_configparser()
        self.assertEqual(o.section.number_float, 8.0)
        self.assertEqual(o.section.number_integer, -9)

    def test_number_env(self):
        self.setup_env()
        o = self.parse()
        self.assertEqual(o.section.number_float, -6.5)
        self.assertEqual(o.section.number_integer, -6)

    def test_integer_exceptions(self):
        self.setup_number('test')
        self.assertRaises(ops.exceptions.ValidationError, self.parse)
        # Minimum value
        self.setup_number(21)
        self.assertRaises(ops.exceptions.ValidationError, self.parse)
        # Maximum value
        self.setup_number(-21)
        self.assertRaises(ops.exceptions.ValidationError, self.parse)

    def test_string_default(self):
        o = self.parse()
        self.assertEqual(o.section.string, 'string')

    def test_string_optparse(self):
        o = self.parse(['--section-string', 'test'])
        self.assertEqual(o.section.string, 'test')

    def test_string_configparser(self):
        o = self.setup_configparser()
        self.assertEqual(o.section.string, 'config.string')

    def test_string_env(self):
        self.setup_env()
        o = self.parse()
        self.assertEqual(o.section.string, 'env.string')

    def test_string_exceptions(self):
        # Minimum length
        self.setup_string('t')
        self.assertRaises(ops.exceptions.ValidationError, self.parse)
        # Maximum length
        self.setup_string('t' * 16)
        self.assertRaises(ops.exceptions.ValidationError, self.parse)

if __name__ == '__main__':
    unittest.main()
