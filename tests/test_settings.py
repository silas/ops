import os
import unittest
import ops.settings

class Settings(ops.settings.Settings):

    class Section(ops.settings.Section):
        boolean_false = ops.settings.Boolean(default=False)
        boolean_true = ops.settings.Boolean(default=True)
        float = ops.settings.Number(default=1.5)
        integer = ops.settings.Integer(default=1)
        string = ops.settings.String(default='string')

class SettingsTestCase(unittest.TestCase):

    _env = {
        'APP_SECTION_BOOLEAN_FALSE': 'true',
        'APP_SECTION_BOOLEAN_TRUE': 'false',
        'APP_SECTION_FLOAT': '+10.5',
        'APP_SECTION_INTEGER': '-10',
        'APP_SECTION_STRING': 'env.string',
    }

    def setUp(self):
        os.environ.clear()
        self.name = 'app'

    def setup_env(self):
        for name, value in self._env.items():
            os.environ[name] = value

    def setup_configparser(self):
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, 'assets', 'test.cfg')
        return self.parse(config_file=path)

    def parse(self, *args, **kwargs):
        return Settings(name=self.name).parse(*args, **kwargs)

    @property
    def options(self):
        return self.parse()

    def test_boolean_default(self):
        o = self.options
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
        o = self.options
        self.assertEqual(o.section.boolean_false, True)
        self.assertEqual(o.section.boolean_true, False)

    def test_float_default(self):
        o = self.options
        self.assertEqual(o.section.float, 1.5)

    def test_float_optparse(self):
        o = self.parse(['--section-float', '+11.5'])
        self.assertEqual(o.section.float, 11.5)

    def test_float_configparser(self):
        o = self.setup_configparser()
        self.assertEqual(o.section.float, 12.5)

    def test_float_env(self):
        self.setup_env()
        o = self.options
        self.assertEqual(o.section.float, 10.5)

    def test_integer_default(self):
        o = self.options
        self.assertEqual(o.section.integer, 1)

    def test_integer_optparse(self):
        o = self.parse(['--section-integer', '+11.5'])
        self.assertEqual(o.section.integer, 11)

    def test_integer_configparser(self):
        o = self.setup_configparser()
        self.assertEqual(o.section.integer, -12)

    def test_integer_env(self):
        self.setup_env()
        o = self.options
        self.assertEqual(o.section.integer, -10)

    def test_number_default(self):
        o = self.options
        self.assertEqual(o.section.float, 1.5)
        self.assertEqual(o.section.integer, 1)

    def test_number_optparse(self):
        o = self.parse(['--section-float', '-11.5', '--section-integer', '+11'])
        self.assertEqual(o.section.float, -11.5)
        self.assertEqual(o.section.integer, 11)

    def test_number_configparser(self):
        o = self.setup_configparser()
        self.assertEqual(o.section.integer, -12)
        self.assertEqual(o.section.float, 12.5)

    def test_number_env(self):
        self.setup_env()
        o = self.options
        self.assertEqual(o.section.float, 10.5)
        self.assertEqual(o.section.integer, -10)

    def test_string_default(self):
        o = self.options
        self.assertEqual(o.section.string, 'string')

    def test_string_optparse(self):
        o = self.parse(['--section-string', 'test'])
        self.assertEqual(o.section.string, 'test')

    def test_string_configparser(self):
        o = self.setup_configparser()
        self.assertEqual(o.section.string, 'config.string')

    def test_string_env(self):
        self.setup_env()
        o = self.options
        self.assertEqual(o.section.string, 'env.string')

if __name__ == '__main__':
    unittest.main()
