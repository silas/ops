# Copyright (c) 2010, Silas Sewell
# All rights reserved.
#
# This file is subject to the New BSD License (see the LICENSE file).

import copy
import inspect
import os
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
    # Use self if class and no_clas is not true
    print locals['self']
    if not no_class and 'self' in locals:
        locals = locals['self'].__dict__
    # Get or create directory stack variable
    path = ''
    success = False
    if DIRECTORY_STACK_NAME in locals:
        # Do popd
        if len(stack) > 0:
            path = stack.pop()
            try:
                os.chdir(path)
                success = True
            except OSError:
                pass
    # Return results with path
    return Objectify({
        '_bool': success,
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
    # Use self if class and no_clas is not true
    if not no_class and 'self' in locals:
        locals = locals['self'].__dict__
    # Get or create directory stack variable
    if DIRECTORY_STACK_NAME not in locals:
        stack = locals[DIRECTORY_STACK_NAME] = []
    else:
        stack = locals[DIRECTORY_STACK_NAME]
    # Do pushd
    success = False
    try:
        stack.append(os.getcwd())
        os.chdir(path)
        success = True
    except OSError:
        stack.pop()
    # Delete variable if empty
    if not locals[DIRECTORY_STACK_NAME]:
        del locals[DIRECTORY_STACK_NAME]
    # Return results with path
    return Objectify({
        '_bool': success,
        'path': path,
    })

def run(command, close_fds=True, shell=True, env=None, set_env=None):
    """Run a shell command and wait for response. The result object will
    resolve to True if result.code == 0 and text results can be retrieved
    from result.stdout and result.stderr.

    run('ls /random-directory')
    """
    if set_env is not None:
        if env is None:
            env = copy.deepcopy(os.environ)
        env.update(set_env)
    ref = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell,
        close_fds=close_fds,
        env=env,
    )
    data = ref.communicate()
    return Objectify({
        '_bool': ref.returncode == 0,
        'code': ref.returncode,
        'stdout': data[0],
        'stderr': data[1],
    })
