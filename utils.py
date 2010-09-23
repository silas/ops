# Copyright (c) 2010, Silas Sewell
# All rights reserved.
#
# This file is subject to the New BSD License (see the LICENSE file).

import copy
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
            successful = chown(p, **kwargs) and successful
    else:
        successful = chown(path, **kwargs)
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

def _find(value, name=None):
    if name is not None and not fnmatch.fnmatch(value, name):
        return False
    return True

def find(path, directory=True, file=True, **kwargs):
    """Find directories and files in the specified path.

    for path in find('/tmp', name='*.py', directory=False):
        print path
    """
    for root_path, dir_list, file_list in os.walk(path):
        if directory and _find(root_path, **kwargs):
            yield root_path
        if file:
            for f in file_list:
                if _find(f, **kwargs):
                    yield os.path.join(root_path, f)

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
