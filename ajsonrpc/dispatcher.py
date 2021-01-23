"""Method name to method mapper.

Dispatcher is a dict-like object which maps method_name to method.
For usage examples see :meth:`~Dispatcher.add_method`

"""
import functools
import collections.abc


class Dispatcher(collections.abc.MutableMapping):

    """Dictionary-like object which maps method_name to method."""

    def __init__(self, prototype=None):
        """ Build method dispatcher.

        Parameters
        ----------
        prototype : object or dict, optional
            Initial method mapping.

        Examples
        --------

        Init object with method dictionary.

        >>> Dispatcher({"sum": lambda a, b: a + b})
        None

        """
        self.method_map = dict()

        if prototype is not None:
            self.add_prototype(prototype)

    def __getitem__(self, key):
        return self.method_map[key]

    def __setitem__(self, key, value):
        self.method_map[key] = value

    def __delitem__(self, key):
        del self.method_map[key]

    def __len__(self):
        return len(self.method_map)

    def __iter__(self):
        return iter(self.method_map)

    def __repr__(self):
        return repr(self.method_map)

    @classmethod
    def extract_methods(cls, prototype, prefix=''):
        return dict(
            (prefix + method, getattr(prototype, method))
            for method in dir(prototype)
            if not method.startswith('_')
        )

    def add_prototype(self, prototype, prefix=''):
        mapping = self.extract_methods(prototype, prefix=prefix) \
            if not isinstance(prototype, collections.Mapping) \
            else prototype
        self.update(mapping)

    def add_class(self, cls, prefix=None):
        """Add class to dispatcher.

        Adds all of the public methods to dispatcher.

        Notes
        -----
            If class has instance methods (e.g. no @classmethod decorator),
            they likely would not work. Use :meth:`~add_object` instead.

        Parameters
        ----------
        cls : type
            class with methods to be added to dispatcher
        prefix : str, optional
            Method prefix. If not present, lowercased class name is used.

        """
        prefix = prefix or cls.__name__.lower() + '.'
        self.update(Dispatcher.extract_methods(cls), prefix=prefix)

    def add_object(self, obj, prefix=None):
        prefix = prefix or obj.__class__.__name__.lower() + '.'
        self.update(Dispatcher.extract_methods(obj), prefix=prefix)

    def add_method(self, f=None, name=None):
        """ Add a method to the dispatcher.

        Parameters
        ----------
        f : callable
            Callable to be added.
        name : str, optional
            Name to register (the default is function **f** name)

        Notes
        -----
        When used as a decorator keeps callable object unmodified.

        Examples
        --------

        Use as method

        >>> d = Dispatcher()
        >>> d.add_method(lambda a, b: a + b, name="sum")
        <function __main__.<lambda>>

        Or use as decorator

        >>> d = Dispatcher()
        >>> @d.add_method
            def mymethod(*args, **kwargs):
                print(args, kwargs)

        Or use as a decorator with a different function name
        >>> d = Dispatcher()
        >>> @d.add_method(name="my.method")
            def mymethod(*args, **kwargs):
                print(args, kwargs)

        """
        if name and not f:
            return functools.partial(self.add_method, name=name)

        self[name or f.__name__] = f
        return f
