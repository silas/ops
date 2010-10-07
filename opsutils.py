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

def chmod(path, value=None, user=None, group=None, other=None, recursive=False):
    """Change file permissions.

    chmod('/tmp/one', 0755)
    """
    successful = True
    value = mode(value)
    if user is not None:
        value.user = user
    if group is not None:
        value.group = group
    if other is not None:
        value.other = other
    if recursive:
        for p in find(path, no_peek=True):
            successful = _chmod(p, value) and successful
    else:
        successful = _chmod(path, value)
    return successful

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
        for p in find(path, no_peek=True):
            successful = _chown(p, **kwargs) and successful
    else:
        successful = _chown(path, **kwargs)
    return successful

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

class _FindRule(object):

    def __init__(self, exclude=False):
        self.exclude = exclude

    def __call__(self, path, stat):
        raise NotImplementedError()

    def render(self, value=True):
        if self.exclude:
            return not value
        return value

class _FindDirectoryRule(_FindRule):

    def __init__(self, value, **kwargs):
        super(_FindDirectoryRule, self).__init__(**kwargs)
        self.value = value

    def __call__(self, path, stat):
        return self.render(stat.directory == self.value)

class _FindFileRule(_FindRule):

    def __init__(self, value, **kwargs):
        super(_FindFileRule, self).__init__(**kwargs)
        self.value = value

    def __call__(self, path, stat):
        return self.render(stat.file == self.value)

class _FindNameRule(_FindRule):

    def __init__(self, pattern, **kwargs):
        super(_FindNameRule, self).__init__(**kwargs)
        self.pattern = pattern

    def __call__(self, path, stat):
        name = os.path.basename(path)
        return self.render(fnmatch.fnmatch(name, self.pattern))

class _FindTimeRule(_FindRule):

    def __init__(self, type, op, time, **kwargs):
        super(_FindTimeRule, self).__init__(**kwargs)
        self.type = type
        self.op = op
        self.time = time

    def __call__(self, path, stat):
        dt = getattr(stat, self.type)
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
        self.path = os.path.realpath(path)
        self.rules = []
        self.no_peek = no_peek
        self.top_down = top_down

    def __iter__(self):
        if self.no_peek and not self.top_down:
            s = stat(self.path)
            s._directory, s._file = True, False
            if self._match(self.path, s):
                yield self.path
        for root_path, dir_list, file_list in os.walk(self.path):
            if self.no_peek and not self.top_down:
                for d in dir_list:
                    path = os.path.join(root_path, d)
                    s = stat(path)
                    s._directory, s._file = True, False
                    if self._match(path, s):
                        yield path
            else:
                s = stat(root_path)
                s._directory, s._file = True, False
                if self._match(root_path, s):
                    yield root_path
            for f in file_list:
                path = os.path.join(root_path, f)
                s = stat(path)
                s._directory, s._file = False, True
                if self._match(os.path.join(root_path, f), s):
                    yield path

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

    def _match(self, path, stat):
        for rule in self.rules:
            if not rule(path, stat):
                return False
        return True

    def filter(self, **kwargs):
        self._add_rule(kwargs)
        return self

    def exclude(self, **kwargs):
        self._add_rule(kwargs, exclude=True)
        return self

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
        return [user(name=name) for name in self.gr_mem]

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

class _ModeBits(object):

    def __init__(self, value=None, read=None, write=None, execute=None):
        self.read = read
        self.write = write
        self.execute = execute
        if isinstance(value, int) and value >= 0 and value <= 7:
            self._set_numeric(value)

    def _set_numeric(self, value):
        self.read = False
        self.write = False
        self.execute = False
        if value == 1:
            self.execute = True
        elif value == 2:
            self.write = True
        elif value == 3:
            self.execute = True
            self.write = True
        elif value == 4:
            self.read = True
        elif value == 5:
            self.execute = True
            self.read = True
        elif value == 6:
            self.read = True
            self.write = True
        elif value == 7:
            self.execute = True
            self.read = True
            self.write = True

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
        return self.data.st_mode

    @property
    def mode(self):
        return mode(self.data.st_mode)

    @property
    def st_ino(self):
        return self.data.st_ino

    @property
    def inode(self):
        return self.data.st_ino

    @property
    def st_dev(self):
        return self.data.st_dev

    @property
    def device(self):
        return self.data.st_dev

    @property
    def st_nlink(self):
        return self.data.st_nlink

    @property
    def nlink(self):
        return self.data.st_nlink

    @property
    def st_uid(self):
        return self.data.st_uid

    @property
    def user(self):
        return user(id=self.data.st_uid)

    @property
    def st_gid(self):
        return self.data.st_gid

    @property
    def group(self):
        return group(id=self.data.st_gid)

    @property
    def st_size(self):
        return self.data.st_size

    @property
    def size(self):
        return self.st_size

    @property
    def st_atime(self):
        return self.data.st_size

    @property
    def atime(self):
        return datetime.datetime.fromtimestamp(self.data.st_atime)

    @property
    def st_mtime(self):
        return self.data.st_mtime

    @property
    def mtime(self):
        return datetime.datetime.fromtimestamp(self.data.st_mtime)

    @property
    def st_ctime(self):
        return self.data.st_ctime

    @property
    def ctime(self):
        return datetime.datetime.fromtimestamp(self.data.st_ctime)

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
        return group(id=self.pw_gid)

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
    'dirs',
    'exit',
    'find',
    'group',
    'mode',
    'mkdir',
    'objectify',
    'popd',
    'pushd',
    'rm',
    'run',
    'stat',
    'user',
    'workspace',
]
