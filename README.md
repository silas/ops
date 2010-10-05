opsutils
============

`opsutils` is a collection of convenience functions intended to augment the
builtin Python `os` and `shutil` modules.

### Requirements

 * Python >= 2.6

### Example

    from opsutils import *

    for path in find('/tmp').filter(name='*.py', file=True).exclude(mtime__day=13):
        print path

### License

This work is licensed under the New BSD License (see the LICENSE file).
