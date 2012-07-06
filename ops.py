# Copyright (c) 2010-2012, Silas Sewell
# All rights reserved.
#
# This file is subject to the MIT License (see the LICENSE file).

__copyright__ = '2010-2012, Silas Sewell'
__version__ = '0.4.4'

import collections
import datetime
import fnmatch
import grp
import logging
import numbers
import os
import pipes
import pwd
import re
import select
import shutil
import stat as stat_
import string
import subprocess
import sys
import tempfile

log = logging.getLogger('ops')
type_ = type

class Error(Exception): pass
class ValidationError(Error): pass

def _chmod(path, value=None):
    try:
        os.chmod(path, value.numeric)
        return True
    except OSError, error:
        log.error('chmod: %s' % error)
    except TypeError:
        log.error('invalid mode value: %s' % value)
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

def _chown(path, uid=-1, gid=-1):
    try:
        os.chown(path, uid, gid)
        return True
    except OSError, error:
        log.error('chown: execute failed: %s (%s)' % (path, error))
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
        elif isinstance(user, numbers.Number):
            user = _ops_user(id=user)
        if isinstance(user, _ops_user):
            if user:
                uid = user.id
            else:
                log.error('chown: unable to get uid')
                successful = False
        else:
            successful = False
    if group is not None:
        if isinstance(group, basestring):
            group = _ops_group(name=group)
        elif isinstance(group, numbers.Number):
            group = _ops_user(id=group)
        if isinstance(group, _ops_group):
            if group:
                gid = group.id
            else:
                log.error('chown: unable to get gid')
                successful = False
        else:
            successful = False
    if not (uid == -1  and gid == -1):
        if recursive:
            for p in find(path, no_peek=True):
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
        if follow_links and os.path.islink(src_path):
            src_path = os.path.realpath(src_path)
        if follow_links and os.path.islink(dst_path):
            dst_path = os.path.realpath(dst_path)
        if os.path.isdir(src_path):
            if not recursive:
                return successful
            shutil.copytree(src_path, dst_path, symlinks=follow_links)
            successful = True
        elif os.path.exists(src_path):
            if os.path.isdir(dst_path):
                dst_path = os.path.join(dst_path, os.path.basename(src_path))
            shutil.copy2(src_path, dst_path)
            successful = True
        else:
            log.error('cp: source not found: %s' % src_path)
    except OSError, error:
        log.error('cp: execute failed: %s => %s (%s)' % (src_path, dst_path, error))
    return successful

class _Env(collections.MutableMapping):
    """Get and set environment variables.

      >>> env('PATH')
      '/bin'
      >>> env('TEST', type='number')
      10.0
      >>> env('TEST', type=int)
      10
      >>> env('PATH', '/bin')
      True
      >>> env('PATH', '/sbin', append=True)
      True
      >>> env('PATH')
      '/bin:/sbin'
      >>> env('PATH', '/sbin', prepend=True, sep=':', unique=True)
      False
      >>> env('PATH')
      '/bin:/sbin'
    """

    def __init__(self, data, raise_exception=False):
        self._data = data
        self._raise_exception = raise_exception

    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            return self._data
        elif len(args) == 1:
            return self.get(*args, **kwargs)
        else:
            return self.set(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return self._data.__contains__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self._data.__delitem__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self._data.__getitem__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self._data.__iter__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self._data.__len__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self._data.__setitem__(*args, **kwargs)

    def get(self, name, default=None, type=None, raise_exception=None):
        value = self._data.get(name)
        if raise_exception is None:
            raise_exception = self._raise_exception
        return normalize(value, default, type, raise_exception=raise_exception)

    def set(self, name, value, add=False, append=False, prepend=False, sep=':', unique=False):
        if add and name in self:
            return False
        if not isinstance(value, basestring):
            value = unicode(value)
        if not isinstance(sep, basestring):
            sep = unicode(sep)
        if append or prepend:
            current_value = env.get(name, default='')
            if current_value:
                if unique and sep and value in current_value.split(sep):
                    return False
                if append:
                    self._data[name] = env.get(name, default='') + sep + value
                # Don't prepend if we asked for append and unique
                if prepend and not (append and unique):
                    self._data[name] = value + sep + env.get(name, default='')
            else:
                self._data[name] = value
        else:
            self._data[name] = value
        return True

env = _Env(os.environ)

def exit(code=0, text=''):
    """Exit and print text (if defined) to stderr if code > 0 or stdout
    otherwise.

      >>> exit(code=1, text='Invalid directory path')
    """
    if not isinstance(text, basestring):
        text = unicode(text)
    if code > 0:
        if text:
            print >> sys.stderr, text
        sys.exit(code)
    else:
        if text:
            print text
        sys.exit(0)

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
        name = os.path.basename(path)
        return self.render(fnmatch.fnmatch(name, self.pattern))

class _FindTimeRule(_FindRule):

    def __init__(self, type, op, time, **kwargs):
        super(_FindTimeRule, self).__init__(**kwargs)
        self.type = type
        self.op = op
        self.time = time

    def __call__(self, path):
        dt = getattr(path.stat, self.type)
        if not self.op or self.op == 'exact':
            if isinstance(self.time, datetime.date):
                return self.render(dt.year == self.time.year and
                        dt.month == self.time.month and
                        dt.day == self.time.day)
            return self.render(dt == self.time)
        if isinstance(self.time, datetime.date) and not isinstance(self.time, datetime.datetime):
            time = datetime.datetime(year=self.time.year, month=self.time.month, day=self.time.day)
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
            self.path = os.path.realpath(path)
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
        for root_path, dir_list, file_list in os.walk(self.path, topdown=self.top_down):
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
                log.error('unknown find rule %s=%s' % (name, value))

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
            self._id = os.getegid()

    def __nonzero__(self):
        if self._bool is None:
            self.data
        return self._bool

    @property
    def data(self):
        if not hasattr(self, '_data'):
            try:
                if self._name:
                    self._data = grp.getgrnam(self._name)
                else:
                    self._data = grp.getgrgid(self._id)
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
        return [user(name=name) for name in self.gr_mem]
_ops_group = group

def mkdir(path, recursive=True):
    """Create a directory at the specified path. By default this function
    recursively creates the path.

      >>> if mkdir('/tmp/one/two'):
      ...     print 'OK'
      OK
    """
    if os.path.exists(path):
        return True
    try:
        if recursive:
            os.makedirs(path)
        else:
            os.mkdir(path)
    except OSError, error:
        log.error('mkdir: execute failed: %s (%s)' % (path, error))
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
            log.warning('mode: unknown bit: %s' % value)
        if not hasattr(self, name):
            setattr(self, name, _ModeBits())

    @property
    def numeric(self):
        mode = 0
        for type_name, type_abbr in self._TYPES:
            type_value = getattr(self, type_name)
            for bits_name, bits_abbr in self._BITS:
                if getattr(type_value, bits_name):
                    mode |= getattr(stat_, 'S_I%s%s' % (bits_abbr, type_abbr))
        return mode

    @numeric.setter
    def numeric(self, mode):
        for type_name, type_abbr in self._TYPES:
            type_value = getattr(self, type_name)
            for bits_name, bits_abbr in self._BITS:
                value = bool(mode & getattr(stat_, 'S_I%s%s' % (bits_abbr, type_abbr)))
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
    NUMBER_RE = re.compile('^[-+]?(([0-9]+\.?[0-9]*)|([0-9]*\.?[0-9]+))$')
    if type is None and default is None:
        type = basestring
    elif type is None:
        type = type_(default)
    if type in (basestring, 'basestring'):
        if value is not None:
            return value
        if default is None:
            if raise_exception:
                raise ValidationError('invalid string')
            else:
                return ''
    elif type in (str, 'str', 'string'):
        if value is not None:
            return value if isinstance(value, str) else str(value)
        if default is None:
            if raise_exception:
                raise ValidationError('invalid string')
            else:
                return ''
    elif type in (unicode, 'unicode'):
        if value is not None:
            return value if isinstance(value, unicode) else unicode(value)
        if default is None:
            if raise_exception:
                raise ValidationError('invalid string')
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
                raise ValidationError('invalid boolean')
            else:
                return False
    elif type in (numbers.Number, 'number'):
        if value is not None:
            if value.isdigit():
                return int(value)
            elif NUMBER_RE.match(value):
                return eval(value)
        if default is None:
            if raise_exception:
                raise ValidationError('invalid number')
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
                    raise ValidationError('invalid number')
                else:
                    return 0
    elif type in (float, 'float'):
        if value is not None and NUMBER_RE.match(value):
            return float(value)
        if default is None:
            if raise_exception:
                raise ValidationError('invalid number')
            else:
                return 0.0
    return default

class obj(collections.MutableMapping):
    """Use property access syntax to retrieve values from a dict-like object.

      >>> o = obj({'name': 'hello', 'value': 'world'})
      >>> o.name
      'hello'
      >>> o.value
      'world'
      >>> o.one.two = 3
      >>> o
      {'name': 'hello', 'value': 'world', 'one': {'two': 3}}
      >>> o = obj({'name': 'hello'}, default=None)
      >>> o.name
      'test'
      >>> o.value
      None
    """

    def __init__(self, data=None, **kwargs):
        self._data = data or {}
        self._bool = kwargs.get('bool')
        self._default = 'default' in kwargs
        self._grow = kwargs.get('grow', True)
        if self._default:
            self._grow = False
            self._value = kwargs['default']

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            if self._default:
                return self._value
            raise AttributeError(name)

    def __contains__(self, *args, **kwargs):
        return self._data.__contains__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self._data.__delitem__(*args, **kwargs)

    def __getitem__(self, name, *args, **kwargs):
        if name not in self._data and self._grow:
            self._data[name] = obj()
        return self._data.__getitem__(name, *args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self._data.__iter__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self._data.__len__(*args, **kwargs)

    def __nonzero__(self, *args, **kwargs):
        if self._bool is not None:
            return self._bool
        else:
            return bool(self._data)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super(obj, self).__setattr__(name, value)
        else:
            self._data[name] = value

    def __setitem__(self, *args, **kwargs):
        return self._data.__setitem__(*args, **kwargs)

    def __repr__(self):
        return repr(self._data)

    def __str__(self):
        return str(self._data)

    def __unicode__(self):
        return unicode(self._data)

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
            value = os.path.join(root, name)
        try:
            value = os.path.realpath(value)
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
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
        else:
            if os.path.isfile(path):
                os.remove(path)
            else:
                os.rmdir(path)
    except OSError, error:
        log.error('rm: execute failed: %s (%s)' % (path, error))
        return False
    return True

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
      echo 'Some $%^$## "" + '"'"' content'
    """
    env = None
    if 'env' in kwargs:
        if kwargs.get('env_empty'):
            env = {}
        else:
            env = copy.deepcopy(os.environ)
        env.update(kwargs['env'])
    combine = kwargs.get('combine', False)
    stdout = kwargs.get('stdout', False)
    stderr = kwargs.get('stderr', False)
    if stdout is True:
        stdout = sys.stdout.write
    if stderr is True:
        stderr = sys.stderr.write
    if kwargs:
        args = {}
        q = pipes.quote
        for name, value in kwargs.items():
            if isinstance(value, basestring):
                args[name] = q(value)
            elif isinstance(value, (list, tuple)):
                args[name] = u' '.join([q(unicode(v)) for v in value])
            elif isinstance(value, dict):
                args[name] = u' '.join([u'%s %s' % (q(n), q(v)) for n, v in value.items()])
            else:
                args[name] = pipes.quote(unicode(value))
        command = string.Template(command).safe_substitute(args)
    log.debug('run: %s' % command)
    ref = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT if combine is True else subprocess.PIPE,
        shell=kwargs.get('shell', True),
        close_fds=kwargs.get('close_fds', True),
        env=env,
        cwd=kwargs.get('cwd', tempfile.gettempdir()),
    )
    fds = [ref.stdout]
    if combine is not True:
        fds.append(ref.stderr)
    stdout_result = ''
    stderr_result = ''
    while fds:
        for fd in select.select(fds, tuple(), tuple())[0]:
            line = fd.readline()
            if line:
                if fd == ref.stdout:
                    if stdout:
                        stdout(line)
                    stdout_result += line
                elif fd == ref.stderr:
                    if stderr:
                        stderr(line)
                    stderr_result += line
            else:
                fds.remove(fd)
    ref.wait()
    return obj({
        'code': ref.returncode,
        'command': command,
        'stdout': stdout_result,
        'stderr': stderr_result,
    }, bool=ref.returncode == 0, grow=False)

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
            self._data = os.stat(self.path)
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
        return user(id=self.data[4])

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
        return datetime.datetime.fromtimestamp(self.data[7])

    @property
    def st_mtime(self):
        return self.data[8]

    @property
    def mtime(self):
        return datetime.datetime.fromtimestamp(self.data[8])

    @property
    def st_ctime(self):
        return self.data[9]

    @property
    def ctime(self):
        return datetime.datetime.fromtimestamp(self.data[9])

    @property
    def file(self):
        if not hasattr(self, '_file'):
            self._file = os.path.isfile(self.path)
        return self._file

    @property
    def directory(self):
        if not hasattr(self, '_directory'):
            self._directory = os.path.isdir(self.path)
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
            self._id = os.geteuid()

    def __nonzero__(self):
        if self._bool is None:
            self.data
        return self._bool

    @property
    def data(self):
        if not hasattr(self, '_data'):
            try:
                if self._name:
                    self._data = pwd.getpwnam(self._name)
                else:
                    self._data = pwd.getpwuid(self._id)
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
        self._path = tempfile.mkdtemp(suffix=self.suffix, prefix=self.prefix)
        return self

    def __exit__(self, type, value, traceback):
        if self.path and os.path.exists(self.path):
            chmod(self.path, 0700, recursive=True)
            rm(self.path, recursive=True)

    @property
    def path(self):
        return self._path

    def join(self, *args):
        return os.path.join(self.path, *args)

__all__ = [
    'chmod',
    'chown',
    'cp',
    'env',
    'exit',
    'find',
    'group',
    'mode',
    'mkdir',
    'normalize',
    'obj',
    'path',
    'rm',
    'run',
    'stat',
    'user',
    'workspace',
]
