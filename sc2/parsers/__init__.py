class P(object):
    def __init__(self, name, type, length=None, min_value=None, max_value=None):
        if callable(type):
            type = type()
        self.name, self.type = name, type
        self.length = length
        self.min_value, self.max_value = min_value, max_value

class BitParser(object):
    structs = []
    
    def serialize(self, fp, **kwargs):
        for data in self.structs:
            if not isinstance(data, P):
                data = P(*data)
            print data.name
            value = data.type.serialize(
                fp,
                length=data.length,
                min_value=data.min_value,
                max_value=data.max_value,
            )
            setattr(self, data.name, value)
        return self

    def __repr__(self):
        return u"<%s: %s>" % (self.__class__.__name__, unicode(self))

    def __str__(self):
        return str([n[0] for n in self.structs])

class AsciiString(BitParser):
    def serialize(self, fp, length, **kwargs):
        length = fp.readbits(length)
        return fp.read(length >> 3)

UnicodeString = AsciiString

class Integer(BitParser):
    def serialize(self, fp, length, **kwargs):
        return fp.readbits(length)

class List(BitParser):
    def __init__(self, type):
        self.type = type

    def serialize(self, fp, length, min_value=None, max_value=None, **kwargs):
        value = fp.readbits(length)
        if min_value:
            assert value >= min_value, "exceeded min value of %s (was %s)" % (min_value, value)
        if max_value:
            assert value <= max_value, "exceeded max value of %s (was %s)" % (max_value, value)
        values = []
        for n in range(value):
            values.append(self.type().serialize(fp))
        return values

class Nullable(BitParser):
    def serialize(self, fp, length, **kwargs):
        present = fp.readbits(1)
        if present:
            return fp.readbits(length)

class Boolean(BitParser):
    def serialize(self, fp, **kwargs):
        return bool(fp.readbits(1))

class Byte(BitParser):
    def serialize(self, fp, length, **kwargs):
        return fp.readbits(length)

class Enum(BitParser):
    choices = []
    
    def __init__(self, *choices):
        self.choices = choices
        
    def serialize(self, fp, length, **kwargs):
        return self.choices[fp.readbits(length)]


class FixedString(BitParser):
    # Length is in bytes
    def serialize(self, fp, length, **kwargs):
        return fp.read(length)

class Hash(BitParser):
    def serialize(self, fp, length, **kwargs):
        return binascii.hexlify(fp.read(length))