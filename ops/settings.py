import optparse
import numbers
import ops.exceptions
import ops.utils

class Type(object):

    def __init__(self, default=None, required=True, type=None, optparse=True, optparse_opts=None):
        self.default = default
        self.required = required
        self.type = type
        self.optparse = optparse
        self.optparse_opts = optparse_opts

    def env_value(self, prefix='', suffix='', type=None):
        name = [self.name]
        if prefix:
            name.insert(0, prefix)
        if suffix:
            name.append(suffix)
        name = '_'.join(name).upper()
        value = ops.utils.env_get(name, default=self.default, type=self.type)
        if value is None or value == self.default:
            return
        return value

    @property
    def optparse_dest(self):
        return '%s_%s' % (self.section._name, self.name)

    def optparse_add(self, parser):
        if not self.optparse_opts:
            self.optparse_opts = [
                '--%s' % '-'.join([self.section._name, self.name]) if self.section._name else self.name
            ]
        kwargs = {
            'dest': self.optparse_dest,
        }
        if self.default is not None:
            kwargs['default'] = self.default
        parser.add_option(*self.optparse_opts, **kwargs)

    def optparse_value(self, options):
        if options is None:
            return
        value = unicode(getattr(options, self.optparse_dest))
        value = ops.utils.normalize(value, default=self.default, type=self.type)
        if value is None or value == self.default:
            return
        return value

    def validate(self, value):
        if self.required and value is None:
            raise ops.exceptions.ValidationError('required')

class Number(Type):

    def __init__(self, default=None, required=True, type='number'):
        super(Number, self).__init__(default=default, required=required, type=type)

    def validate(self, value):
        super(Number, self).validate(value)
        if value is None:
            return
        if not isinstance(value, numbers.Number):
            raise ops.exceptions.ValidationError('not a number')

class String(Type):

    def __init__(self, default=None, required=True, type='basestring'):
        super(String, self).__init__(default=default, required=required, type=type)

    def validate(self, value):
        super(String, self).validate(value)
        if value is None:
            return
        if not isinstance(value, basestring):
            raise ops.exceptions.ValidationError('not a string')

class Section(object):

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

    def __call__(self, optparse_options=None):
        options = {}
        for name, option in self.objects.items():
            value = option.optparse_value(optparse_options)
            if value is None:
                value = option.env_value(prefix='_'.join([self._options.name, self._name]) if self._options.name else self.name)
            if value is None:
                value = option.default
            option.validate(value)
            options[name] = value
        return ops.utils.objectify(options)

class Settings(object):

    def __init__(self, name='', environment=True, optparse=True):
        self._command_line = None
        self._sections = None
        self.name = name
        self.environment = environment
        self.optparse = optparse

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
                for option in section.objects.values():
                    option.optparse_add(self._command_line)
        return self._command_line

    def command_line_parse(self):
        return self.command_line.parse_args()

    def parse(self, args=None):
        sections = {}

        optparse_options = None
        optparse_args = None

        if self.optparse:
            optparse_options, optparse_args = self.command_line.parse_args(args)

        for name, section in self.sections.items():
            sections[name] = section(optparse_options=optparse_options)

        return ops.utils.objectify(sections)
