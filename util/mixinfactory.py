class MixinFactory(object):
    """Methods to extend functionality at runtime"""
    @classmethod
    def extend(cls, obj, mixin, name=None):
        if name is None:
            name = obj.__class__.__name__
        base = obj.__class__
        obj.__class__ = cls.extendtype(base, mixin, name)
        return obj
    
    @classmethod
    def extendtype(cls, base, mixin, name=None):
        if name is None:
            name = base.__name__
        return type(name, (mixin, base), {})