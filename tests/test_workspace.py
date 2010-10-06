import helper

import os
import unittest
import opsutils

class WorkspaceTestCase(unittest.TestCase):

    def test_with(self):
        prefix = 'prefix-'
        suffix = '-suffix'
        path = None
        with opsutils.workspace(suffix=suffix, prefix=prefix) as w:
            path = w.path
            name = os.path.basename(w.path)
            self.assertTrue(os.path.isdir(path))
            self.assertTrue(name.startswith(prefix))
            self.assertTrue(name.endswith(suffix))
        self.assertFalse(os.path.exists(path))

if __name__ == '__main__':
    unittest.main()
