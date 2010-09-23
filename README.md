python-utils
============

python-utils is a collection of convenience functions intended to augment the
builtin Python `os` and `shutil` modules.

### Requirements

 * Python >= 2.6

### Examples

#### cp

    cp('/etc/passwd', '/tmp')

#### exit

    exit(code=1, text='Invalid directory path')

#### find

    for path in find('/tmp', name='*.pyc', directory=False):
        print 'Deleting %s...' % path
        rm(path)

#### pushd & popd

    pushd('/tmp')
    popd()

#### mkdir

    mkdir('/tmp/build/hello-world')

#### rm

    rm('/tmp/build', recursive=True)

#### run

    r = run("du -sh ${path} | awk '{ print $1 }'", path='/tmp')
    print 'Result (%s): %s' % (r.code, r.stdout.strip())
    >>> Result(0): 14M
    bool(r)
    >>> True

    r = run('ls /fail-dir')
    print 'Result (%s): %s' % (r.code, r.stderr.strip())
    >>> Result(2): ls: cannot access /fail-dir: No such file or directory
    bool(r)
    >>> False

### License

This work is licensed under the New BSD License (see the LICENSE file).
