import helper

import os
import unittest
import ops

class WorkspaceTestCase(unittest.TestCase):

    def test_with(self):
        prefix = 'prefix-'
        suffix = '-suffix'
        path = None
        with ops.workspace(suffix=suffix, prefix=prefix) as w:
            path = w.path
            name = os.path.basename(w.path)
            self.assertTrue(os.path.isdir(path))
            self.assertTrue(name.startswith(prefix))
            self.assertTrue(name.endswith(suffix))
        self.assertFalse(os.path.exists(path))

    def test_bad_permissions(self):
        path = None
        name = 'test'
        with ops.workspace() as w:
            path = w.path
            ops.mkdir(w.join(name))
            ops.chmod(w.path, 0000)
            self.assertTrue(os.path.isdir(path))
        self.assertFalse(os.path.exists(path))

if __name__ == '__main__':
    unittest.main()
