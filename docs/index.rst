.. opsutils documentation master file, created by
   sphinx-quickstart on Mon Oct  4 21:50:09 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ops
===

ops is a collection of Python modules and tools that makes building and
running system applications a little easier.

Settings
--------

Lets say we create ``hello.py`` with the following code::

   from ops import exceptions, settings, utils

   class Settings(settings.Settings):

       class General(settings.Section):
           debug = settings.Boolean(default=False, help='enable debugging')

       class Http(settings.Section):
           cookie_secret = settings.String(min_length=8, max_length=32, help='key to encrypt HTTP cookies')

       class Database(settings.Section):
           host = settings.String(default='localhost', help='MySQL database host')
           port = settings.Integer(default=3306, min_value=0, help='MySQL database port')

   try:
       settings = Settings('TestServer').parse()
   except exceptions.ValidationError, error:
       utils.exit(code=1, text=error)

   print 'Debug: %s' % settings.general.debug
   print 'Cookie secret: %s' % settings.http.cookie_secret
   print 'Database host: %s' % settings.database.host
   print 'Database port: %s' % settings.database.port

If we run ``python hello.py --help`` we'll get the following::

   Usage: hello.py [options]

   Options:
     -h, --help            show this help message and exit
     -c FILE               read configuration from FILE

     database:
       --database-host=DATABASE_HOST
                           MySQL database host
       --database-port=DATABASE_PORT
                           MySQL database port

     http:
       --http-cookie-secret=HTTP_COOKIE_SECRET
                           key to encrypt HTTP cookies

     general:
       --general-debug     enable debugging

If we then create ``hello.cfg`` with the following content::

   [http]
   cookie_secret = not.a.good.pass

And run ``python hello.py -c hello.cfg`` we should see::

   Debug: False
   Cookie secret: not.a.good.pass
   Database host: localhost
   Database port: 3306

If we run ``export TESTSERVER_GENERAL_DEBUG=true`` then
``python hello.py -c hello.cfg --database-host=mysql`` we should get::

   Debug: True
   Cookie secret: not.a.good.pass
   Database host: mysql
   Database port: 3306

.. currentmodule:: ops.settings
.. autoclass:: Settings
   :members: parse
.. autoclass:: Section
.. autoclass:: Boolean
.. autoclass:: Float
.. autoclass:: Integer
.. autoclass:: Number
.. autoclass:: String

Utils
-----

.. currentmodule:: ops.utils
.. autofunction:: chmod
.. autofunction:: chown
.. autofunction:: cp
.. autofunction:: env_get
.. autofunction:: env_has
.. autofunction:: env_set
.. autofunction:: exit
.. autofunction:: find
.. autofunction:: group
.. autofunction:: mkdir
.. autofunction:: mode
.. autofunction:: normalize
.. autofunction:: objectify
.. autofunction:: path
.. autofunction:: rm
.. autofunction:: run
.. autofunction:: stat
.. autofunction:: user
.. autofunction:: workspace

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
