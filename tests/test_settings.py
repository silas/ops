import os
import unittest
import ops.settings

class Settings(ops.settings.Settings):

    class Database(ops.settings.Section):
        type = ops.settings.String(default='sqlite3')
        port = ops.settings.Number(default=0)

class SettingsTestCase(unittest.TestCase):

    _env = {
        'TEST_DATABASE_TYPE': 'mysql',
        'TEST_DATABASE_PORT': '2',
    }

    def setUp(self):
        os.environ.clear()
        self.name = 'test'

    def setup_env(self):
        for name, value in self._env.items():
            os.environ[name] = value

    def parse(self, args=None):
        return Settings(name=self.name).parse(args)

    @property
    def options(self):
        return self.parse()

    def test_number(self):
        o = self.options
        self.assertEqual(o.database.port, 0)

        o = self.parse(['--database-port', '1'])
        self.assertEqual(o.database.port, 1)

        self.setup_env()
        o = self.options
        self.assertEqual(o.database.port, 2)

    def test_string(self):
        o = self.options
        self.assertEqual(o.database.type, 'sqlite3')

        o = self.parse(['--database-type', 'psql'])
        self.assertEqual(o.database.type, 'psql')

        self.setup_env()
        o = self.options
        self.assertEqual(o.database.type, 'mysql')

if __name__ == '__main__':
    unittest.main()
