# Copyright (c) 2011, OpsDojo Inc.
# All rights reserved.
#
# This file is subject to the MIT License (see the LICENSE file).

import ConfigParser
import optparse
import numbers
import ops.exceptions
import ops.utils

class Type(object):
    """An abstract configuration option, override for custom types."""

    def __init__(self, default=None, required=True, type=None, help=None, optparse_opts=None, optparse_metavar=None):
        self.default = default
        self.required = required
        self.type = type
        self.help = help
        self.optparse_opts = optparse_opts
        self.optparse_metavar = optparse_metavar

    def env_value(self, prefix='', suffix=''):
        """Retrieved and normalize the value of an environment variable.

        The name of the variable retrieved is uppercase
        ``prefix + self.name + suffix``.
        """
        name = [self.name]
        if prefix:
            name.insert(0, prefix)
        if suffix:
            name.append(suffix)
        name = '_'.join(name).upper()
        if not ops.utils.env_has(name):
            return
        try:
            return ops.utils.env_get(name, type=self.type, raise_exception=True)
        except ops.exceptions.ValidationError:
            return ops.utils.env_get(name)

    def configparser_value(self, parser):
        """Retrieve and normalize the value of option ``self.name`` in section
        ``self.section._name`` from an ini file.

            [section]
            option = value
        """
        if parser.has_option(self.section._name, self.name):
            value = parser.get(self.section._name, self.name)
            if value is None:
                return
            try:
                return ops.utils.normalize(value, type=self.type, raise_exception=True)
            except ops.exceptions.ValidationError:
                return value

    @property
    def optparse_dest(self):
        return '%s_%s' % (self.section._name, self.name)

    def optparse_add(self, parser, action='store'):
        """Add an option to an optparse parser in the format
        ``--section-option=value`` in which all underscores are replaced with
        dashes.
        """
        if not self.optparse_opts:
            name = '--%s' % '-'.join([self.section._name, self.name]) if self.section._name else self.name
            self.optparse_opts = [name.replace('_', '-')]
        kwargs = {'action': action, 'dest': self.optparse_dest}
        if self.help is not None:
            kwargs['help'] = self.help
        if self.optparse_metavar is not None:
            kwargs['metavar'] = self.optparse_metavar
        parser.add_option(*self.optparse_opts, **kwargs)

    def optparse_value(self, options):
        """Retrieve and normalize an option from the results of optparse."""
        value = getattr(options, self.optparse_dest)
        if value is None:
            return value
        try:
            return ops.utils.normalize(unicode(value), type=self.type, raise_exception=True)
        except ops.exceptions.ValidationError:
            return value

    def validate(self, value):
        """Validate the value of type.

        You can extend this to add additional validators.
        """
        if self.required and value is None:
            raise ops.exceptions.ValidationError('required')

class Boolean(Type):
    """A boolean option."""

    def __init__(self, **kwargs):
        kwargs['type'] = kwargs.get('type', 'boolean')
        super(Boolean, self).__init__(**kwargs)

    def validate(self, value):
        super(Boolean, self).validate(value)
        if value is None:
            return
        if not isinstance(value, bool):
            raise ops.exceptions.ValidationError('not a boolean')

    def optparse_add(self, *args, **kwargs):
        kwargs['action'] = 'store_false' if self.default else 'store_true'
        super(Boolean, self).optparse_add(*args, **kwargs)

class NumberMixin(object):

    def init(self, kwargs):
        self.min_value = kwargs.pop('min_value', None)
        self.max_value = kwargs.pop('max_value', None)
        return kwargs

    def validate(self, value):
        if self.min_value is not None and value < self.min_value:
            raise ops.exceptions.ValidationError('less than %s' % self.min_value)
        if self.max_value is not None and value > self.max_value:
            raise ops.exceptions.ValidationError('more than %s' % self.max_value)

class Float(Type, NumberMixin):
    """A float option."""

    def __init__(self, **kwargs):
        kwargs['type'] = kwargs.get('type', 'float')
        kwargs = NumberMixin.init(self, kwargs)
        Type.__init__(self, **kwargs)

    def validate(self, value):
        super(Float, self).validate(value)
        if value is None:
            return
        if not isinstance(value, float):
            raise ops.exceptions.ValidationError('not a float')
        NumberMixin.validate(self, value)

class Integer(Type, NumberMixin):
    """An integer option."""

    def __init__(self, **kwargs):
        kwargs['type'] = kwargs.get('type', 'integer')
        kwargs = NumberMixin.init(self, kwargs)
        Type.__init__(self, **kwargs)

    def validate(self, value):
        super(Integer, self).validate(value)
        if value is None:
            return
        if not isinstance(value, int):
            raise ops.exceptions.ValidationError('not an integer')
        NumberMixin.validate(self, value)

class Number(Type, NumberMixin):
    """A number option.

    This should be able to parse and validate any Python number.
    """

    def __init__(self, **kwargs):
        kwargs['type'] = kwargs.get('type', 'number')
        kwargs = NumberMixin.init(self, kwargs)
        Type.__init__(self, **kwargs)

    def validate(self, value):
        super(Number, self).validate(value)
        if value is None:
            return
        if not isinstance(value, numbers.Number):
            raise ops.exceptions.ValidationError('not a number')
        NumberMixin.validate(self, value)

class String(Type):
    """A string option."""

    def __init__(self, **kwargs):
        kwargs['type'] = kwargs.get('type', 'basestring')
        self.min_length = kwargs.pop('min_length', None)
        self.max_length = kwargs.pop('max_length', None)
        super(String, self).__init__(**kwargs)

    def validate(self, value):
        super(String, self).validate(value)
        if value is None:
            return
        if not isinstance(value, basestring):
            raise ops.exceptions.ValidationError('not a string')
        if self.min_length is not None and len(value) < self.min_length:
            raise ops.exceptions.ValidationError('less than %s characters long' % self.min_length)
        if self.max_length is not None and len(value) > self.max_length:
            raise ops.exceptions.ValidationError('more than %s characters long' % self.max_length)

class Section(object):
    """A collection of similar options."""

    def __init__(self, options, name):
        self._options = options
        self._name = name
        self._objects = None

    @property
    def objects(self):
        if self._objects is None:
            self._objects = {}
            for name in self.__class__.__dict__:
                if not name.startswith('_'):
                    obj = self.__class__.__dict__[name]
                    if isinstance(obj, Type):
                        obj.name = name.lower()
                        obj.section = self
                        self._objects[obj.name] = obj
        return self._objects

    def __call__(self, configparser_options=None, env=None, optparse_options=None):
        options = {}
        if configparser_options and not configparser_options.has_section(self._name):
            configparser_options = None

        for name, option in self.objects.items():
            value = None
            if optparse_options:
                value = option.optparse_value(optparse_options)
            if value is None and configparser_options:
                value = option.configparser_value(configparser_options)
            if value is None and env:
                value = option.env_value(prefix='_'.join([self._options.name, self._name]) if self._options.name else self._name)
            if value is None:
                value = option.default
            try:
                option.validate(value)
            except ops.exceptions.ValidationError, error:
                raise ops.exceptions.ValidationError('%s in %s is %s' % (name, self._name, error))
            options[name] = value

        return ops.utils.objectify(options)

    def _meta(self, name, default=None):
        if hasattr(self, 'Meta') and hasattr(self.Meta, name):
            return getattr(self.Meta, name)
        return default

    def _optparse_group(self, parser):
        if self.objects:
            group_args = [self._meta('name', self._name)]
            if self._meta('description'):
                group_args.append(self._meta('description'))
            group = optparse.OptionGroup(parser, *group_args)
            for option in self.objects.values():
                option.optparse_add(group)
            return group

class Settings(object):
    """This class defines your application settings and should be filled with
    various sections."""

    def __init__(self, name='', env=True, optparse=True, configparser=True):
        self._command_line = None
        self._sections = None
        self.name = name
        self.env = env
        self.optparse = optparse
        self.configparser = configparser

    @property
    def sections(self):
        if self._sections is None:
            self._sections = {}
            for name in self.__class__.__dict__:
                if not name.startswith('_'):
                    obj = self.__class__.__dict__[name]
                    if issubclass(obj, Section):
                        self._sections[name.lower()] = obj(self, name.lower())
        return self._sections

    @property
    def command_line(self):
        if self._command_line is None:
            self._command_line = optparse.OptionParser()
            for section in self.sections.values():
                group = section._optparse_group(self._command_line)
                if group is not None:
                    self._command_line.add_option_group(group)
        return self._command_line

    def parse(self, args=None, config_file=None):
        """Parse and return settings."""
        sections = {}

        configparser_options = None
        optparse_options = None
        optparse_args = None

        if self.optparse:
            if self.configparser:
                self.command_line.add_option(
                    '-c',
                    dest='config_file',
                    help='read configuration from FILE',
                    metavar='FILE',
                )
            optparse_options, optparse_args = self.command_line.parse_args(args)
            if config_file is None:
                config_file = optparse_options.config_file

        if config_file:
            try:
                configparser_options = ConfigParser.SafeConfigParser()
                if not configparser_options.read([config_file]):
                    raise ops.exceptions.Error('unable to read %s' % config_file)
            except ConfigParser.ParsingError, error:
                raise ops.exceptions.Error(error)

        for name, section in self.sections.items():
            sections[name] = section(
                configparser_options=configparser_options,
                env=self.env,
                optparse_options=optparse_options,
            )

        return ops.utils.objectify(sections)
