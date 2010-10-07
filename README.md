opsutils
========

[opsutils][opsutils] ([docs][docs]) is a collection of convenience functions
intended to augment the built-in Python [os][os] and [shutil][shutil] modules.

### Requirements

 * Python >= 2.6

### Example

    from opsutils import *

    for path in find('/tmp').filter(name='*.py', file=True).exclude(mtime__day=13):
        chown(path, user='root', group='root')

### License

This work is licensed under the New BSD License (see the LICENSE file).

[opsutils]: http://github.com/opsdojo/opsutils/raw/master/opsutils.py
[docs]: http://opsdojo.github.com/opsutils
[os]: http://docs.python.org/library/os.html
[shutil]: http://docs.python.org/library/shutil.html
