python-utils
============

python-utils is a collection of Python utilities.

#### exit

    exit(code=1, text='Invalid directory path')

#### pushd & popd

    pushd('/tmp')
    popd

### run

    r = run("du -sh /tmp | awk '{ print $1 }'")
    print 'Result (%s): %s' % (r.code, r.stderr.strip())
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
