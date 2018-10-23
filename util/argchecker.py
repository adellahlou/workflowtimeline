class ArgChecker:
    """Utilities to check arguments"""
    
    @classmethod
    def KwargsHave(cls, kwargs, required):
        for arg in required:
            if arg not in kwargs:
                raise ValueError("Must pass in named argument '{0}'".format(arg))