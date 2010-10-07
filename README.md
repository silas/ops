opsutils
========

[opsutils][opsutils] is a collection of convenience functions intended to
augment the builtin Python [os][os] and [shutil][shutil] modules.

### Requirements

 * Python >= 2.6

### Example

    from opsutils import *

    for path in find('/tmp').filter(name='*.py', file=True).exclude(mtime__day=13):
        chown(path, user='root', group='root')

### License

This work is licensed under the New BSD License (see the LICENSE file).

[opsutils]: http://github.com/opsdojo/opsutils/raw/master/opsutils.py
[os]: http://docs.python.org/library/os.html
[shutil]: http://docs.python.org/library/shutil.html
