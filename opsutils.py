# Copyright (c) 2010, Silas Sewell
# All rights reserved.
#
# This file is subject to the New BSD License (see the LICENSE file).

import copy
import datetime
import fnmatch
import glob
import grp
import inspect
import logging as logginglib
import os
import pipes
import pwd
import shutil
import string
import subprocess
import stat as statlib
import sys
import tempfile

logging = logginglib.getLogger('opsutils')

DIRECTORY_STACK_NAME = '__utils_directory_stack'

def _chmod(path, value=None):
    if isinstance(value, int):
        value = mode(value)
    try:
        os.chmod(path, value.numeric)
        return True
    except OSError, error:
        logging.error('chmod: %s' % error)
    except TypeError:
        logging.error('invalid mode value: %s' % value)
    return False

def chmod(path, mode=None, user=None, group=None, other=None, recursive=False):
    """Change file permissions.

    chmod('/tmp/one', 0755)
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

def _chown(path, **kwargs):
    user = kwargs.get('user')
    group = kwargs.get('group')
    uid = kwargs.get('uid', -1)
    gid = kwargs.get('gid', -1)
    successful = True
    if uid == -1 and user is not None:
        try:
            uid = pwd.getpwnam(user)[2]
        except KeyError:
            logging.error('chown: uid lookup failed: %s' % user)
            successful = False
    if gid == -1 and group is not None:
        try:
            gid = grp.getgrnam(group)[2]
        except KeyError:
            logging.error('chown: gid lookup failed: %s' % group)
            successful = False
    try:
        os.chown(path, uid, gid)
    except OSError, error:
        logging.error('chown: execute failed: %s (%s)' % (path, error))
        successful = False
    return successful

def chown(path, **kwargs):
    """Change file owner and group.

    chown('/tmp/one', user='root', group='apache')
    """
    successful = True
    recursive = kwargs.get('recursive')
    if recursive:
        for p in _ops_find(path, no_peek=True):
            successful = _chown(p, **kwargs) and successful
    else:
        successful = _chown(path, **kwargs)
    return successful
_ops_chown = chown

def cp(src_path, dst_path, follow_links=False, recursive=True):
    """Copy source to destination.

    cp('/tmp/one', '/tmp/two')
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
            logging.error('cp: source not found: %s' % src_path)
    except OSError, error:
        logging.error('cp: execute failed: %s => %s (%s)' % (src_path, dst_path, error))
    return successful
_ops_cp = cp

def dirs(no_class=False):
    """Return the directory stack from pushd/popd.

    dirs()
    """
    # Get locals from caller
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    locals = calframe[1][0].f_locals
    # Use self if caller is a method and no_class is false
    if not no_class and 'self' in locals:
        locals = locals['self'].__dict__
    # Get or create directory stack variable
    if DIRECTORY_STACK_NAME not in locals:
        stack = locals[DIRECTORY_STACK_NAME] = []
    else:
        stack = locals[DIRECTORY_STACK_NAME]
    return stack
_ops_dirs = dirs

def exit(code=0, text=''):
    """Exit and print text (if defined) to stderr if code > 0 or stdout
    otherwise.

    exit(code=1, text='Invalid directory path')
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
_ops_exit = exit

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

    for path in find('/tmp').filter(name='*.py', file=True).exclude(mtime__day=13):
        print path
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
    """Helper class for getting information about a group.

    g = group(id=0)
    print g.name
    """

    def __init__(self, id=None, name=None):
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
        return [_ops_user(name=name) for name in self.gr_mem]
_ops_group = group

def mkdir(path, recursive=True):
    """Create a directory at the specified path. By default this function
    recursively creates the structure.

    mkdir('/tmp/build')
    """
    if os.path.exists(path):
        return True
    try:
        if recursive:
            os.makedirs(path)
        else:
            os.mkdir(path)
    except OSError, error:
        logging.error('mkdir: execute failed: %s (%s)' % (path, error))
        return False
    return True
_ops_mkdir = mkdir

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

    mode(0755).user.read
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
                    mode |= getattr(statlib, 'S_I%s%s' % (bits_abbr, type_abbr))
        return mode

    @numeric.setter
    def numeric(self, mode):
        for type_name, type_abbr in self._TYPES:
            type_value = getattr(self, type_name)
            for bits_name, bits_abbr in self._BITS:
                value = bool(mode & getattr(statlib, 'S_I%s%s' % (bits_abbr, type_abbr)))
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

class objectify(dict):

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __nonzero__(self):
        try:
            return self['_bool']
        except KeyError:
            return len(self) > 0

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
_ops_objectify = objectify

def _path_stat_get(self):
    if not hasattr(self, '_stat'):
        self._stat = _ops_stat(self)
    return self._stat

def _path_stat_set(self, value=None):
    if isinstance(value, _ops_stat):
        self._stat = stat

class path(unicode):
    """An object for representing paths.

    path('/tmp').stat.owner.name
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
_ops_path = path

def popd(no_class=False):
    """Remove last path from the stack and make it the current working
    directory. By default popd will look for the stack variable in self if
    in a method and the local scope if in a function. The class behaviour can
    be disabled by passing no_class=True.

    popd()
    """
    # Get locals from caller
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    locals = calframe[1][0].f_locals
    # Use self if caller is a method and no_class is false
    if not no_class and 'self' in locals:
        locals = locals['self'].__dict__
    # Get or create directory stack variable
    path = ''
    successful = False
    if DIRECTORY_STACK_NAME in locals:
        stack = locals[DIRECTORY_STACK_NAME]
        # Do popd
        if len(stack) > 0:
            path = stack.pop()
            try:
                os.chdir(path)
                successful = True
            except OSError:
                logging.error('popd: unable to chdir: %s' % path)
        else:
            logging.error('popd: stack empty')
    else:
        logging.error('popd: stack does not exist')
    # Return results with path
    return objectify({
        '_bool': successful,
        'path': path,
    })
_ops_popd = popd

def pushd(path, no_class=False):
    """Add the current working directory to the stack and switch to the path
    specified. By default pushd will attach the the stack variable to self if
    in a method and the local scope if in a function. The class behaviour can
    be disabled by passing no_class=True.

    pushd('/tmp')
    """
    # Get locals from caller
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    locals = calframe[1][0].f_locals
    # Use self if caller is a method and no_class is false
    if not no_class and 'self' in locals:
        locals = locals['self'].__dict__
    # Get or create directory stack variable
    if DIRECTORY_STACK_NAME not in locals:
        stack = locals[DIRECTORY_STACK_NAME] = []
    else:
        stack = locals[DIRECTORY_STACK_NAME]
    # Do pushd
    successful = False
    try:
        stack.append(os.getcwd())
        os.chdir(path)
        successful = True
    except OSError:
        logging.error('pushd: unable to chdir: %s' % path)
        stack.pop()
    # Delete variable if empty
    if not locals[DIRECTORY_STACK_NAME]:
        del locals[DIRECTORY_STACK_NAME]
    # Return results with path
    return objectify({
        '_bool': successful,
        'path': path,
    })
_ops_pushd = pushd

def rm(path, recursive=False):
    """Delete a specified file or directory. This function does not recursively
    delete by default.

    rm('/tmp/build', recursive=True)
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
        logging.error('rm: execute failed: %s (%s)' % (path, error))
        return False
    return True
_ops_rm = rm

def run(command, **kwargs):
    """Run a shell command and wait for the response. The result object will
    resolve to True if result.code == 0 and output/error results can be
    retrieved from result.stdout and result.stderr variables.

    run('ls ${path}', path='/tmp')
    """
    env = None
    if 'env' in kwargs:
        if kwargs.get('env_empty'):
            env = {}
        else:
            env = copy.deepcopy(os.environ)
        env.update(kwargs['env'])
    if kwargs:
        args = {}
        for name, value in kwargs.items():
            if not isinstance(value, basestring):
                value = unicode(value)
            args[name] = pipes.quote(value)
        command = string.Template(command).safe_substitute(args)
    logging.debug('run: %s' % command)
    ref = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=kwargs.get('shell', True),
        close_fds=kwargs.get('close_fds', True),
        env=env,
        cwd=kwargs.get('cwd', tempfile.gettempdir()),
    )
    data = ref.communicate()
    return objectify({
        '_bool': ref.returncode == 0,
        'code': ref.returncode,
        'command': command,
        'stdout': data[0],
        'stderr': data[1],
    })
_ops_rm = rm

class stat(object):

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
    """Helper class for getting information about a user.

    u = user(id=0)
    print u.name
    """

    def __init__(self, id=None, name=None):
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
    cleaned up. `workspace` takes the same parameters as `tempfile.mkdtemp`.

    with workspace('test') as w:
        print w.join('dir1', 'file1')
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self._path = None

    def __enter__(self):
        self._path = tempfile.mkdtemp(*self.args, **self.kwargs)
        return self

    def __exit__(self, type, value, traceback):
        if self.path and os.path.exists(self.path):
            _ops_chmod(self.path, 0700, recursive=True)
            _ops_rm(self.path, recursive=True)

    @property
    def path(self):
        return self._path

    def join(self, *args):
        return os.path.join(self.path, *args)
_ops_workspace = workspace

__all__ = [
    'chmod',
    'chown',
    'cp',
    'dirs',
    'exit',
    'find',
    'group',
    'mode',
    'mkdir',
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
