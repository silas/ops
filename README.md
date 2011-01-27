ops
===

ops is a collection of Python modules and tools that makes building and
running system applications a little easier.

### Requirements

 * Python >= 2.6

### Example

    from ops.utils import *

    for path in find('/tmp').filter(name='*.py', file=True).exclude(mtime__day=13):
        result = run('python ${path}', path=path)
        print 'Command: %s' % result.command
        print 'Code: %s' % result.code
        if result:
            print 'Stdout: %s' % result.stdout
        else:
            print 'Stderr: %s' % result.stderr

Which might produce something like:

    Command: python /tmp/test.py
    Code: 0
    Stdout: Hello World

### License

This work is licensed under the MIT License (see the LICENSE file).
