opsutils
========

[opsutils][opsutils] is a collection of convenience functions intended to
augment the built-in Python [os][os] and [shutil][shutil] modules.

### Requirements

 * Python >= 2.6

### Example

    from opsutils import *

    for path in find('/tmp').filter(name='*.py', file=True).exclude(mtime__day=13):
        result = run('python ${path}', path=path)
        print 'Command: %s' % result.command
        print 'Code: %s' % result.code
        if result:
            print 'Stdout: %s' % result.stdout
        else:
            print 'Stderr: %s' % result.stderr

Which would produce a result like:

    Command: python /tmp/test.py
    Code: 0
    Stdout: Hello World

### License

This work is licensed under the New BSD License (see the LICENSE file).

[opsutils]: http://github.com/opsdojo/opsutils/raw/master/opsutils.py
[os]: http://docs.python.org/library/os.html
[shutil]: http://docs.python.org/library/shutil.html
