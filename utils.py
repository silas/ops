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
import logging
import os
import pipes
import pwd
import shutil
import string
import subprocess
import sys
import tempfile

DIRECTORY_STACK_NAME = '__utils_directory_stack'

class Objectify(dict):

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
        for p in find(path):
            successful = _chown(p, **kwargs) and successful
    else:
        successful = _chown(path, **kwargs)
    return successful

def cp(src_path, dst_path, follow_symlinks=False):
    """Copy source to destination.

    cp('/tmp/one', '/tmp/two')
    """
    successful = False
    try:
        if follow_symlinks and os.path.islink(src_path):
            src_path = os.path.realpath(src_path)
        if follow_symlinks and os.path.islink(dst_path):
            dst_path = os.path.realpath(dst_path)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, symlinks=follow_symlinks)
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

def _find_relative(stat, time):
    if isinstance(time, datetime.datetime) and time == stat:
        return True
    elif isinstance(time, datetime.date) and time == stat.date():
        return True
    elif isinstance(time, datetime.timedelta):
        if time > 0 and stat >= datetime.datetime.now() + time:
            return True
        elif time < 0 and stat <= datetime.datetime.now() + (-time):
            return True
    return False

def _find_between(stat, low, high):
    if isinstance(low, datetime.date):
        low = datetime.datetime(year=low.year, month=low.month, day=low.day)
    if isinstance(high, datetime.date):
        high = datetime.datetime(year=high.year, month=high.month, day=high.day)
    if low is not None and high is not None:
        return stat >= low and stat <= high
    elif low is not None:
        return stat >= low
    elif high is not None:
        return stat <= high
    return True

def _find(value, stat, **kwargs):
    if 'name' in kwargs and not fnmatch.fnmatch(value, kwargs['name']):
        return False
    for n in ('atime', 'ctime', 'mtime'):
        s = getattr(stat, n)
        # check relative time
        if n in kwargs and not _find_relative(s, kwargs[n]):
            return False
        # check between low/high
        if (('%s_low' % n in kwargs or '%s_high' % n in kwargs) and
            not _find_between(s, kwargs.get('%s_low' % n),
                kwargs.get('%s_high' % n))):
            return False
    return True

def find(path, directory=True, file=True, **kwargs):
    """Find directories and files in the specified path.

    for path in find('/tmp', name='*.py', directory=False):
        print path
    """
    path = os.path.realpath(path)
    for root_path, dir_list, file_list in os.walk(path):
        if directory:
            d_name = os.path.basename(root_path)
            d_stat = stat(root_path)
            if _find(d_name, d_stat, **kwargs):
                yield root_path
        if file:
            for f in file_list:
                f_path = os.path.join(root_path, f)
                f_stat = stat(f_path)
                if _find(f, f_stat, **kwargs):
                    yield os.path.join(root_path, f)

class group(object):
    """Helper class for getting information about a group.

    g = group(id=0)
    print g.name
    """

    def __init__(self, id=None, name=None):
        self._id = id
        self._name = name
        if id is None and name is None:
            self._id = os.getegid()

    @property
    def data(self):
        if not hasattr(self, '_data'):
            if self._name:
                try:
                    self._data = grp.getgrnam(self._name)
                except KeyError:
                    logging.error('unable to lookup by name: %s' % self._name)
                    self._data = [None] * 7
            else:
                try:
                    self._data = grp.getgrgid(self._id)
                except KeyError:
                    logging.error('unable to lookup by gid: %s' % self._id)
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
    return Objectify({
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
    return Objectify({
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
            args[name] = pipes.quote(value)
        command = string.Template(command).safe_substitute(args)
    logging.debug('run: %s' % command)
    ref = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        close_fds=True,
        env=env,
    )
    data = ref.communicate()
    return Objectify({
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
        return self.data[0]

    @property
    def st_ino(self):
        return self.data[1]

    @property
    def inode(self):
        return self.st_ino

    @property
    def st_dev(self):
        return self.data[2]

    @property
    def device(self):
        return self.st_dev

    @property
    def st_nlink(self):
        return self.data[3]

    @property
    def nlink(self):
        return self.st_nlinks

    @property
    def st_uid(self):
        return self.data[4]

    @property
    def user(self):
        return user(id=self.st_uid)

    @property
    def st_gid(self):
        return self.data[5]

    @property
    def gid(self):
        return self.st_gid

    @property
    def st_size(self):
        return self.data[6]

    @property
    def size(self):
        return self.st_size

    @property
    def st_atime(self):
        return self.data[7]

    @property
    def atime(self):
        return datetime.datetime.fromtimestamp(self.st_atime)

    @property
    def st_mtime(self):
        return self.data[8]

    @property
    def mtime(self):
        return datetime.datetime.fromtimestamp(self.st_mtime)

    @property
    def st_ctime(self):
        return self.data[9]

    @property
    def ctime(self):
        return datetime.datetime.fromtimestamp(self.st_ctime)

class user(object):
    """Helper class for getting information about a user.

    u = user(id=0)
    print u.name
    """

    def __init__(self, id=None, name=None):
        self._id = id
        self._name = name
        if id is None and name is None:
            self._id = os.geteuid()

    @property
    def data(self):
        if not hasattr(self, '_data'):
            if self._name:
                try:
                    self._data = pwd.getpwnam(self._name)
                except KeyError:
                    logging.error('unable to lookup by name: %s' % self._name)
                    self._data = [None] * 7
            else:
                try:
                    self._data = pwd.getpwuid(self._id)
                except KeyError:
                    logging.error('unable to lookup by uid: %s' % self._id)
                    self._data = [None] * 7
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
            rm(self.path, recursive=True)

    @property
    def path(self):
        return self._path

    def join(self, *args):
        return os.path.join(self.path, *args)
