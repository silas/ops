from distutils.core import setup
from ops import __version__ as version

long_description = """
ops is a library for scripting systems administration tasks in Python.

You can find the latest docs at http://silas.sewell.org/ops/.
"""

setup(
    name='ops',
    version=version,
    description='Library for scripting systems administration tasks',
    long_description=long_description.strip(),
    author='Silas Sewell',
    author_email='silas@sewell.org',
    license='MIT',
    url='https://github.com/silas/ops',
    py_modules=['ops'],
    classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Systems Administration',
    ],
)
