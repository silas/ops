# Copyright (c) 2010-2011, OpsDojo Inc.
# All rights reserved.
#
# This file is subject to the MIT License (see the LICENSE file).

_m = __import__

logging = _m('logging').getLogger('ops')
type_ = type

def _chmod(path, value=None):
    if isinstance(value, int):
        value = mode(value)
    try:
        _m('os').chmod(path, value.numeric)
        return True
    except OSError, error:
        logging.error('chmod: %s' % error)
    except TypeError:
        logging.error('invalid mode value: %s' % value)
    return False

def chmod(path, mode=None, user=None, group=None, other=None, recursive=False):
    """Changes file mode bits.

      >>> if chmod('/tmp/one', 0755):
      ...     print 'OK'
      OK

    NOTE: The precending ``0`` is required when using a numerical mode.
    """
    successful = True
    mode = _ops_mode(mode)
    if user is not None:
        mode.user = user
    if group is not None:
        mode.group = group
    if other is not None:
        mode.other = other
    if recursive:
        for p in find(path, no_peek=True):
            successful = _chmod(p, mode) and successful
    else:
        successful = _chmod(path, mode)
    return successful
_ops_chmod = chmod

def _chown(path, uid=-1, gid=-1):
    try:
        _m('os').chown(path, uid, gid)
        return True
    except OSError, error:
        logging.error('chown: execute failed: %s (%s)' % (path, error))
    return False

def chown(path, user=None, group=None, recursive=False):
    """Change file owner and group.

      >>> if chown('/tmp/one', user='root', group='wheel'):
      ...     print 'OK'
      OK
    """
    successful = True
    uid = -1
    gid = -1
    if user is not None:
        if isinstance(user, basestring):
            user = _ops_user(name=user)
        elif isinstance(user, int):
            user = _ops_user(id=user)
        if isinstance(user, _ops_user):
            if user:
                uid = user.id
            else:
                logging.error('chown: unable to get uid')
                successful = False
        else:
            successful = False
    if group is not None:
        if isinstance(group, basestring):
            group = _ops_group(name=group)
        elif isinstance(group, int):
            group = _ops_user(id=group)
        if isinstance(group, _ops_group):
            if group:
                gid = group.id
            else:
                logging.error('chown: unable to get gid')
                successful = False
        else:
            successful = False
    if not (uid == -1  and gid == -1):
        if recursive:
            for p in _ops_find(path, no_peek=True):
                successful = _chown(p, uid=uid, gid=gid) and successful
        else:
            successful = _chown(path, uid=uid, gid=gid)
    else:
        successful = False
    return successful

def cp(src_path, dst_path, follow_links=False, recursive=True):
    """Copy source to destination.

      >>> if cp('/tmp/one', '/tmp/two'):
      ...     print 'OK'
      OK
    """
    successful = False
    try:
        if follow_links and _m('os').path.islink(src_path):
            src_path = _m('os').path.realpath(src_path)
        if follow_links and _m('os').path.islink(dst_path):
            dst_path = _m('os').path.realpath(dst_path)
        if _m('os').path.isdir(src_path):
            if not recursive:
                return successful
            _m('shutil').copytree(src_path, dst_path, symlinks=follow_links)
            successful = True
        elif _m('os').path.exists(src_path):
            if _m('os').path.isdir(dst_path):
                dst_path = _m('os').path.join(dst_path, _m('os').path.basename(src_path))
            _m('shutil').copy2(src_path, dst_path)
            successful = True
        else:
            logging.error('cp: source not found: %s' % src_path)
    except OSError, error:
        logging.error('cp: execute failed: %s => %s (%s)' % (src_path, dst_path, error))
    return successful

def env_get(name, default=None, type=None, raise_exception=False):
    """Get environment variable.

      >>> env_get('PATH')
      '/bin'
      >>> env_get('TEST', type='number')
      10.0
      >>> env_get('TEST', type=int)
      10
    """
    exists = env_has(name)
    value = _m('os').environ.get(name)
    return normalize(value, default, type, raise_exception=raise_exception)

def env_has(name):
    """Check if environment variable exists.

      >>> env_has('PATH')
      True
    """
    return name in _m('os').environ

def env_set(name, value, add=False, append=False, prepend=False, sep=':', unique=False):
    """Set environment variable.

      >>> env_set('PATH', '/bin')
      True
      >>> env_set('PATH', '/sbin', append=True)
      True
      >>> env_get('PATH')
      '/bin:/sbin'
      >>> env_set('PATH', '/sbin', prepend=True, sep=':', unique=True)
      False
      >>> env_get('PATH')
      '/bin:/sbin'
    """
    if add and env_has(name):
        return False
    if not isinstance(value, basestring):
        value = unicode(value)
    if not isinstance(sep, basestring):
        sep = unicode(sep)
    if append or prepend:
        current_value = env_get(name, default='')
        if current_value:
            if unique and sep and value in current_value.split(sep):
                return False
            if append:
                _m('os').environ[name] = env_get(name, default='') + sep + value
            # Don't prepend if we asked for append and unique
            if prepend and not (append and unique):
                _m('os').environ[name] = value + sep + env_get(name, default='')
        else:
            _m('os').environ[name] = value
    else:
        _m('os').environ[name] = value
    return True

def exit(code=0, text=''):
    """Exit and print text (if defined) to stderr if code > 0 or stdout
    otherwise.

      >>> exit(code=1, text='Invalid directory path')
    """
    if not isinstance(text, basestring):
        text = unicode(text)
    if code > 0:
        if text:
            print >> _m('sys').stderr, text
        _m('sys').exit(code)
    else:
        if text:
            print text
        _m('sys').exit(0)

class _FindRule(object):

    def __init__(self, exclude=False):
        self.exclude = exclude

    def __call__(self, path):
        raise NotImplementedError()

    def render(self, value=True):
        if self.exclude:
            return not value
        return value

class _FindDirectoryRule(_FindRule):

    def __init__(self, value, **kwargs):
        super(_FindDirectoryRule, self).__init__(**kwargs)
        self.value = value

    def __call__(self, path):
        return self.render(path.stat.directory == self.value)

class _FindFileRule(_FindRule):

    def __init__(self, value, **kwargs):
        super(_FindFileRule, self).__init__(**kwargs)
        self.value = value

    def __call__(self, path):
        return self.render(path.stat.file == self.value)

class _FindNameRule(_FindRule):

    def __init__(self, pattern, **kwargs):
        super(_FindNameRule, self).__init__(**kwargs)
        self.pattern = pattern

    def __call__(self, path):
        name = _m('os').path.basename(path)
        return self.render(_m('fnmatch').fnmatch(name, self.pattern))

class _FindTimeRule(_FindRule):

    def __init__(self, type, op, time, **kwargs):
        super(_FindTimeRule, self).__init__(**kwargs)
        self.type = type
        self.op = op
        self.time = time

    def __call__(self, path):
        dt = getattr(path.stat, self.type)
        if not self.op or self.op == 'exact':
            if isinstance(self.time, _m('datetime').date):
                return self.render(dt.year == self.time.year and
                        dt.month == self.time.month and
                        dt.day == self.time.day)
            return self.render(dt == self.time)
        if isinstance(self.time, _m('datetime').date) and not isinstance(self.time, _m('datetime').datetime):
            time = _m('datetime').datetime(year=self.time.year, month=self.time.month, day=self.time.day)
        else:
            time = self.time
        if self.op == 'lt':
            return self.render(dt < time)
        elif self.op == 'lte':
            return self.render(dt <= time)
        elif self.op == 'gt':
            return self.render(dt > time)
        elif self.op == 'gte':
            return self.render(dt >= time)
        elif self.op == 'year':
            return self.render(dt.year == self.time)
        elif self.op == 'month':
            return self.render(dt.month == self.time)
        elif self.op == 'day':
            return self.render(dt.day == self.time)
        elif self.op == 'hour':
            return self.render(dt.hour == self.time)
        elif self.op == 'minute':
            return self.render(dt.minute == self.time)
        elif self.op == 'second':
            return self.render(dt.second == self.time)
        return self.render()

class find(object):
    """Find directories and files in the specified path.

      >>> for path in find('/tmp').filter(name='*.py', file=True).exclude(mtime__year=2010):
      ...     print '%s is owned by %s' % (path, path.stat.user.name)
      /tmp/test1.py is owned by silas
      /tmp/test2.py is owned by root
    """

    def __init__(self, path, no_peek=False, top_down=False):
        try:
            self.path = _m('os').path.realpath(path)
        except OSError:
            self.path = None
        self.rules = []
        self.no_peek = no_peek
        self.top_down = top_down

    def __iter__(self):
        if self.path is None:
            return
        if self.no_peek and not self.top_down:
            p = path(self.path)
            if self._match(p):
                yield p
        for root_path, dir_list, file_list in _m('os').walk(self.path, topdown=self.top_down):
            if self.no_peek and not self.top_down:
                for d in dir_list:
                    p = path(root=self.path, name=d)
                    if self._match(p):
                        yield p
            else:
                p = path(root_path)
                if self._match(p):
                    yield p
            for f in file_list:
                p = path(root=root_path, name=f)
                if self._match(p):
                    yield p

    def _add_rule(self, data, exclude=False):
        for name, value in data.items():
            n, p, op = name.partition('__')
            if n == 'name':
                self.rules.append(_FindNameRule(value, exclude=exclude))
            elif n == 'directory':
                self.rules.append(_FindDirectoryRule(value, exclude=exclude))
            elif n == 'file':
                self.rules.append(_FindFileRule(value, exclude=exclude))
            elif n in ('atime', 'ctime', 'mtime'):
                self.rules.append(_FindTimeRule(n, op, value, exclude=exclude))
            else:
                logging.error('unknown find rule %s=%s' % (name, value))

    def _match(self, path):
        for rule in self.rules:
            if not rule(path):
                return False
        return True

    def filter(self, **kwargs):
        self._add_rule(kwargs)
        return self

    def exclude(self, **kwargs):
        self._add_rule(kwargs, exclude=True)
        return self
_ops_find = find

class group(object):
    """Get information about a group.

      >>> group(id=0).name
      'root'
      >>> group(name='root').id
      0
    """

    def __init__(self, name=None, id=None):
        self._id = id
        self._name = name
        self._bool = None
        if id is None and name is None:
            self._id = _m('os').getegid()

    def __nonzero__(self):
        if self._bool is None:
            self.data
        return self._bool

    @property
    def data(self):
        if not hasattr(self, '_data'):
            try:
                if self._name:
                    self._data = _m('grp').getgrnam(self._name)
                else:
                    self._data = _m('grp').getgrgid(self._id)
                self._bool = True
            except KeyError:
                self._bool = False
                self._data = [None] * 7
        return self._data

    @property
    def gr_name(self):
        return self.data[0]

    @property
    def name(self):
        return self.gr_name

    @property
    def gr_passwd(self):
        return self.data[1]

    @property
    def gr_gid(self):
        return self.data[2]

    @property
    def id(self):
        return self.gr_gid

    @property
    def gr_mem(self):
        return self.data[3]

    @property
    def members(self):
        return [_ops_user(name=name) for name in self.gr_mem]
_ops_group = group

def mkdir(path, recursive=True):
    """Create a directory at the specified path. By default this function
    recursively creates the path.

      >>> if mkdir('/tmp/one/two'):
      ...     print 'OK'
      OK
    """
    if _m('os').path.exists(path):
        return True
    try:
        if recursive:
            _m('os').makedirs(path)
        else:
            _m('os').mkdir(path)
    except OSError, error:
        logging.error('mkdir: execute failed: %s (%s)' % (path, error))
        return False
    return True

class _ModeBits(object):

    def __init__(self, value=None, read=None, write=None, execute=None):
        self.read = read
        self.write = write
        self.execute = execute
        if isinstance(value, int) and value >= 0 and value <= 7:
            self._set_numeric(value)

    def _set_numeric(self, value):
        self.execute = value & 1
        self.read = value & 4
        self.write = value & 2

class mode(object):
    """An object for representing file mode bits.

      >>> m = mode(0755)
      >>> m.user.read
      True
      >>> m.group.execute
      True
      >>> m.other.write
      False
    """

    _TYPES = (('user', 'USR'), ('group', 'GRP'), ('other', 'OTH'))
    _BITS = (('read', 'R'), ('write', 'W'), ('execute', 'X'))

    bits = _ModeBits

    def __init__(self, value=None, user=None, group=None, other=None):
        self.user = user
        self.group = group
        self.other = other
        if isinstance(value, int):
            self.numeric = value

    def _set_bits(self, name, value):
        if isinstance(value, int):
            setattr(self, name, _ModeBits(value=value))
        elif isinstance(value, _ModeBits):
            setattr(self, name, value)
        elif value is not None:
            logging.warning('mode: unknown bit: %s' % value)
        if not hasattr(self, name):
            setattr(self, name, _ModeBits())

    @property
    def numeric(self):
        mode = 0
        for type_name, type_abbr in self._TYPES:
            type_value = getattr(self, type_name)
            for bits_name, bits_abbr in self._BITS:
                if getattr(type_value, bits_name):
                    mode |= getattr(_m('stat'), 'S_I%s%s' % (bits_abbr, type_abbr))
        return mode

    @numeric.setter
    def numeric(self, mode):
        for type_name, type_abbr in self._TYPES:
            type_value = getattr(self, type_name)
            for bits_name, bits_abbr in self._BITS:
                value = bool(mode & getattr(_m('stat'), 'S_I%s%s' % (bits_abbr, type_abbr)))
                setattr(type_value, bits_name, value)

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value=None):
        self._set_bits('_user', value)

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value=None):
        self._set_bits('_group', value)

    @property
    def other(self):
        return self._other

    @other.setter
    def other(self, value=None):
        self._set_bits('_other', value)
_ops_mode = mode

def normalize(value, default=None, type=None, raise_exception=False):
    """Convert string variables to a specified type.

      >>> normalize('true', type='boolean')
      True
      >>> normalize('11', type='number')
      11
      >>> normalize('10.3', default=11.0)
      10.3
    """
    NUMBER_RE = _m('re').compile('^[-+]?(([0-9]+\.?[0-9]*)|([0-9]*\.?[0-9]+))$')
    if type is None and default is None:
        type = basestring
    elif type is None:
        type = type_(default)
    if type in (basestring, 'basestring'):
        if value is not None:
            return value
        if default is None:
            if raise_exception:
                raise _m('ops').exceptions.ValidationError('invalid string')
            else:
                return ''
    elif type in (str, 'str', 'string'):
        if value is not None:
            return value if isinstance(value, str) else str(value)
        if default is None:
            if raise_exception:
                raise _m('ops').exceptions.ValidationError('invalid string')
            else:
                return ''
    elif type in (unicode, 'unicode'):
        if value is not None:
            return value if isinstance(value, unicode) else unicode(value)
        if default is None:
            if raise_exception:
                raise _m('ops').exceptions.ValidationError('invalid string')
            else:
                return u''
    elif type in (bool, 'bool', 'boolean'):
        if value is not None:
            value = value.lower().strip()
            if value in ('1', 'true', 'yes', 'on'):
                return True
            elif value in ('0', 'false', 'no', 'off'):
                return False
        if default is None:
            if raise_exception:
                raise _m('ops').exceptions.ValidationError('invalid boolean')
            else:
                return False
    elif type in (_m('numbers').Number, 'number'):
        if value is not None:
            if value.isdigit():
                return int(value)
            elif NUMBER_RE.match(value):
                return eval(value)
        if default is None:
            if raise_exception:
                raise _m('ops').exceptions.ValidationError('invalid number')
            else:
                return 0
    elif type in (int, 'int', 'integer'):
        try:
            return int(value)
        except Exception:
            if isinstance(value, basestring) and NUMBER_RE.match(value):
                return int(eval(value))
            if default is None:
                if raise_exception:
                    raise _m('ops').exceptions.ValidationError('invalid number')
                else:
                    return 0
    elif type in (float, 'float'):
        if value is not None and NUMBER_RE.match(value):
            return float(value)
        if default is None:
            if raise_exception:
                raise _m('ops').exceptions.ValidationError('invalid number')
            else:
                return 0.0
    return default

class objectify(dict):
    """Use property access syntax to retrieve values from a dict-like object.

      >>> o = objectify({'name': 'hello', 'value': 'world'})
      >>> o.name
      'hello'
      >>> o.value
      'world'
      >>> o = objectify({'name': 'hello'}, default=None)
      >>> o.name
      'test'
      >>> o.value
      None
    """

    def __init__(self, data=None, **kwargs):
        dict.__init__(self, data or {})
        if 'default' in kwargs:
            self['_default'] = kwargs['default']

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            try:
                return self['_default']
            except KeyError:
                raise AttributeError(name)

    def __nonzero__(self):
        try:
            return self['_bool']
        except KeyError:
            if len(self) == 0:
                return False
            for key in self:
                if not key.startswith('_'):
                    return True
            return False

    def __len__(self):
        count = 0
        for key in self:
            if not key.startswith('_'):
                count += 1
        return count

    def __repr__(self):
        return repr(self.dict())

    def __str__(self):
        return str(self.dict())

    def __unicode__(self):
        return unicode(self.dict())

    def dict(self):
        values = {}
        for name, value in self.items():
            if not name.startswith('_'):
                values[name] = value
        return values

def _path_stat_get(self):
    if not hasattr(self, '_stat'):
        self._stat = _ops_stat(self)
    return self._stat

def _path_stat_set(self, value=None):
    if isinstance(value, _ops_stat):
        self._stat = stat

class path(unicode):
    """An object for representing paths.

      >>> p = path('/tmp')
      >>> isinstance(p, unicode)
      True
      >>> p
      /tmp
      >>> p.stat.user.name
      root
    """

    def __new__(cls, value=None, stat=None, root=None, name=None):
        if isinstance(value, path):
            return value
        cls.stat = property(_path_stat_get, _path_stat_set)
        if root is not None and name is not None:
            value = _m('os').path.join(root, name)
        try:
            value = _m('os').path.realpath(value)
        except OSError:
            value = ''
        obj = unicode.__new__(cls, value)
        if isinstance(stat, _ops_stat):
            obj._stat = stat
        return obj

def rm(path, recursive=False):
    """Delete a specified file or directory. This function does not recursively
    delete by default.

      >>> if rm('/tmp/build', recursive=True):
      ...     print 'OK'
      OK
    """
    try:
        if recursive:
            if _m('os').path.isfile(path):
                _m('os').remove(path)
            else:
                _m('shutil').rmtree(path)
        else:
            if _m('os').path.isfile(path):
                _m('os').remove(path)
            else:
                _m('os').rmdir(path)
    except OSError, error:
        logging.error('rm: execute failed: %s (%s)' % (path, error))
        return False
    return True
_ops_rm = rm

def run(command, **kwargs):
    """Run a shell command and wait for the response. The result object will
    resolve to True if result.code == 0 and output/error results can be
    retrieved from result.stdout and result.stderr variables.

      >>> result = run('echo ${content}', content='Some $%^$## "" + \' content')
      >>> result.code
      0
      >>> if result:
      ...     print 'Stdout: %s' % result.stdout
      ... else:
      ...     print 'Stderr: %s' % result.stderr
      Stdout: Some $%^$## "" + ' content
      >>> print result.command
      echo "Some \$%^\$## \"\" + ' content"
    """
    env = None
    if 'env' in kwargs:
        if kwargs.get('env_empty'):
            env = {}
        else:
            env = _m('copy').deepcopy(_m('os').environ)
        env.update(kwargs['env'])
    if kwargs:
        args = {}
        q = _m('pipes').quote
        for name, value in kwargs.items():
            if isinstance(value, basestring):
                args[name] = q(value)
            elif isinstance(value, (list, tuple)):
                args[name] = u' '.join([q(unicode(v)) for v in value])
            elif isinstance(value, dict):
                args[name] = u' '.join([u'%s %s' % (q(n), q(v)) for n, v in value.items()])
            else:
                args[name] = _m('pipes').quote(unicode(value))
        command = _m('string').Template(command).safe_substitute(args)
    logging.debug('run: %s' % command)
    ref = _m('subprocess').Popen(
        command,
        stdout=_m('subprocess').PIPE,
        stderr=_m('subprocess').PIPE,
        shell=kwargs.get('shell', True),
        close_fds=kwargs.get('close_fds', True),
        env=env,
        cwd=kwargs.get('cwd', _m('tempfile').gettempdir()),
    )
    data = ref.communicate()
    return objectify({
        '_bool': ref.returncode == 0,
        'code': ref.returncode,
        'command': command,
        'stdout': data[0],
        'stderr': data[1],
    })

class stat(object):
    """Display stat info for files and directories.

      >>> s = stat('/tmp')
      >>> s.user.name
      'root'
      >>> s.mode.other.write
      True
      >>> s.atime
      datetime.datetime(2010, 10, 7, 19, 54, 21)
      >>> s.size
      4096
    """

    def __init__(self, path):
        self.path = path

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = _m('os').stat(self.path)
        return self._data

    @property
    def st_mode(self):
        return self.data[0]

    @property
    def mode(self):
        return _ops_mode(self.data[0])

    @property
    def st_ino(self):
        return self.data[1]

    @property
    def inode(self):
        return self.data[1]

    @property
    def st_dev(self):
        return self.data[2]

    @property
    def device(self):
        return self.data[2]

    @property
    def st_nlink(self):
        return self.data[3]

    @property
    def nlink(self):
        return self.data[3]

    @property
    def st_uid(self):
        return self.data[4]

    @property
    def user(self):
        return _ops_user(id=self.data[4])

    @property
    def st_gid(self):
        return self.data[5]

    @property
    def group(self):
        return _ops_group(id=self.data[5])

    @property
    def st_size(self):
        return self.data[6]

    @property
    def size(self):
        return self.data[6]

    @property
    def st_atime(self):
        return self.data[7]

    @property
    def atime(self):
        return _m('datetime').datetime.fromtimestamp(self.data[7])

    @property
    def st_mtime(self):
        return self.data[8]

    @property
    def mtime(self):
        return _m('datetime').datetime.fromtimestamp(self.data[8])

    @property
    def st_ctime(self):
        return self.data[9]

    @property
    def ctime(self):
        return _m('datetime').datetime.fromtimestamp(self.data[9])

    @property
    def file(self):
        if not hasattr(self, '_file'):
            self._file = _m('os').path.isfile(self.path)
        return self._file

    @property
    def directory(self):
        if not hasattr(self, '_directory'):
            self._directory = _m('os').path.isdir(self.path)
        return self._directory
_ops_stat = stat

class user(object):
    """Get information about a user.

      >>> u = user(id=0)
      >>> u.name
      'root'
      >>> u.home
      '/root'
      >>> u.shell
      '/bin/bash'
      >>> user(name='root').id
      0
    """

    def __init__(self, name=None, id=None):
        self._id = id
        self._name = name
        self._bool = None
        if id is None and name is None:
            self._id = _m('os').geteuid()

    def __nonzero__(self):
        if self._bool is None:
            self.data
        return self._bool

    @property
    def data(self):
        if not hasattr(self, '_data'):
            try:
                if self._name:
                    self._data = _m('pwd').getpwnam(self._name)
                else:
                    self._data = _m('pwd').getpwuid(self._id)
                self._bool = True
            except KeyError:
                self._data = [None] * 7
                self._bool = False
        return self._data

    @property
    def pw_name(self):
        return self.data[0]

    @property
    def name(self):
        return self.pw_name

    @property
    def pw_password(self):
        return self.data[1]

    @property
    def pw_uid(self):
        return self.data[2]

    @property
    def id(self):
        return self.pw_uid

    @property
    def pw_gid(self):
        return self.data[3]

    @property
    def group(self):
        return _ops_group(id=self.pw_gid)

    @property
    def pw_gecos(self):
        return self.data[4]

    @property
    def gecos(self):
        return self.pw_gecos

    @property
    def pw_dir(self):
        return self.data[5]

    @property
    def home(self):
        return self.pw_dir

    @property
    def pw_shell(self):
        return self.data[6]

    @property
    def shell(self):
        return self.pw_shell
_ops_user = user

class workspace(object):
    """Create a secure and temporary workspace that will be automatically
    cleaned up.

      >>> path = None
      >>> with workspace() as w:
      ...     path = w.path
      ...     print w.join('dir1', 'file1')
      /tmp/tmp8IVxyA/dir1/file1
      >>> os.path.exists(path)
      False
    """

    def __init__(self, suffix='', prefix='tmp', dir=None):
        self.suffix = suffix
        self.prefix = prefix
        self._path = None

    def __enter__(self):
        self._path = _m('tempfile').mkdtemp(suffix=self.suffix, prefix=self.prefix)
        return self

    def __exit__(self, type, value, traceback):
        if self.path and _m('os').path.exists(self.path):
            _ops_chmod(self.path, 0700, recursive=True)
            _ops_rm(self.path, recursive=True)

    @property
    def path(self):
        return self._path

    def join(self, *args):
        return _m('os').path.join(self.path, *args)

__all__ = [
    'chmod',
    'chown',
    'cp',
    'dirs',
    'env_get',
    'env_has',
    'env_set',
    'exit',
    'find',
    'group',
    'mode',
    'mkdir',
    'normalize',
    'objectify',
    'path',
    'popd',
    'pushd',
    'rm',
    'run',
    'stat',
    'user',
    'workspace',
]
