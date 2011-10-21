class BaseHandler(object):
    """
    Abstract base class for handlers.
    """
    def __init__(self, base, cls=None):
        """
        Initialize a new handler to handle `type`.

        :Parameters:
          - `base`: reference to pickler/unpickler
          - `cls`: class for which handler will be used (at restore time)

        """
        self._base = base
        self.cls = cls

    def flatten(self, obj, data):
        """
        Flatten `obj` into a json-friendly form.

        :Parameters:
          - `obj`: object of `type`

        """
        raise NotImplementedError("Abstract method.")

    def restore(self, obj):
        """
        Restores the `obj` to `type`

        :Parameters:
          - `object`: json-friendly object

        """
        raise NotImplementedError("Abstract method.")


_marker = object()


class Registry(object):
    """this registry also account for object mro to find handler

    it also cache decisions

    """
    def __init__(self):
        self.REGISTRY = {}
        self._cache = {}

    def register(self, cls, handler):
        """
        Register handler.

        :Parameters:
          - `cls`: Object class
          - `handler`: `BaseHandler` subclass

        """
        # clear cache.
        # TODO : we could just clear cache for superclasses of cls
        self._cache = {}
        self.REGISTRY[cls] = handler
        return handler

    def unregister(self, cls):
        """
        Unregister hander.

        :Parameters:
          - `cls`: Object class
        """
        if cls in self.REGISTRY:
            # clear cache.
            # TODO : we could just clear cache for superclasses of cls
            self._cache = {}
            del self.REGISTRY[cls]

    def get(self, cls):
        """
        Get the customer handler for `obj` (if any)

        :Parameters:
          - `cls`: class to handle

        """
        handler = self._cache.get(cls, _marker)
        if handler is not _marker:
            return handler

        handler = self.REGISTRY.get(cls, _marker)
        if handler is not _marker:
            self._cache[cls] = handler
            return handler

        # _mro search
        mro = getattr(cls, '__mro__', [])
        to_cache = []
        for super_ in mro:
            to_cache.append(super_)
            handler = self._cache.get(super_, _marker)
            if handler is _marker:
                handler = self.REGISTRY.get(super_, _marker)
            if handler is not _marker:
                # remember
                for c in to_cache:
                    # only for super_class of super_
                    if issubclass(super_, c):
                        self._cache[c] = handler
                return handler
        return None


registry = Registry()
