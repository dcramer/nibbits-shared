class P(object):
    def __init__(self, name, type, length=None, min_value=None, max_value=None):
        if callable(type):
            type = type()
        self.name, self.type = name, type
        self.length = length
        self.min_value, self.max_value = min_value, max_value

class Parser(object):
    structs = []
    
    def serialize(self, fp, **kwargs):
        for data in self.structs:
            if not isinstance(data, P):
                data = P(*data)
            value = data.type.serialize(
                fp,
                length=data.length,
                min_value=data.min_value,
                max_value=data.max_value,
            )
            #print '%s = %s' % (data.name, value)
            setattr(self, data.name, value)
        return self

    def __repr__(self):
        return u"<%s: %s>" % (self.__class__.__name__, unicode(self))

    def __str__(self):
        return str(['%s=%s' % (n[0], getattr(self, n[0])) for n in self.structs])