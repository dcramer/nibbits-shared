from common.parser.base import Parser

from cStringIO import StringIO

import mpq
import struct

class String(Parser):
    def serialize(self, fp, **kwargs):
        value = ''
        r = fp.read(1)
        while r != '\x00':
            value += r
            r = fp.read(1)
        return value

class UInt8(Parser):
    def serialize(self, fp, min_value=None, max_value=None, **kwargs):
        value = ord(struct.unpack('c', fp.read(1))[0])
        if min_value:
            assert value >= min_value, "exceeded min value of %s (was %s)" % (min_value, value)
        if max_value:
            assert value <= max_value, "exceeded max value of %s (was %s)" % (max_value, value)
        return value

class UInt16(Parser):
    def serialize(self, fp, min_value=None, max_value=None, **kwargs):
        value = struct.unpack('h', fp.read(2))[0]
        if min_value:
            assert value >= min_value, "exceeded min value of %s (was %s)" % (min_value, value)
        if max_value:
            assert value <= max_value, "exceeded max value of %s (was %s)" % (max_value, value)
        return value

class UInt32(Parser):
    def serialize(self, fp, min_value=None, max_value=None, **kwargs):
        value = struct.unpack('i', fp.read(4))[0]
        if min_value:
            assert value >= min_value, "exceeded min value of %s (was %s)" % (min_value, value)
        if max_value:
            assert value <= max_value, "exceeded max value of %s (was %s)" % (max_value, value)
        return value

class Byte(Parser):
    def serialize(self, fp, length, min_value=None, max_value=None, **kwargs):
        value = fp.read(length)
        if min_value:
            assert value >= min_value, "exceeded min value of %s (was %s)" % (min_value, value)
        if max_value:
            assert value <= max_value, "exceeded max value of %s (was %s)" % (max_value, value)
        return value

class List(Parser):
    def __init__(self, type, length_type):
        self.type = type
        self.length_type = length_type

    def serialize(self, fp, min_value=None, max_value=None, **kwargs):
        value = self.length_type().serialize(fp, **kwargs)
        if min_value:
            assert value >= min_value, "exceeded min value of %s (was %s)" % (min_value, value)
        if max_value:
            assert value <= max_value, "exceeded max value of %s (was %s)" % (max_value, value)
        values = []
        for n in range(value):
            values.append(self.type().serialize(fp))
        return values

class Player(Parser):
    structs = (
        ('IsUnused', UInt8),
        ('PUnk1', UInt8),
        ('PUnk2', UInt8),
        ('Index', UInt8),
        ('Owner', UInt8),
        ('PUnk3', UInt8),
        ('PUnk4', UInt8),
        ('PUnk5', UInt8),
        ('Color', UInt32),
        ('Race', String),
        ('Index', UInt8),
        ('PUnk6', UInt8),
        ('PUnk7', UInt8),
        ('PUnk1', UInt8),
        ('PUnk9', UInt8),
        ('PUnk10', UInt8),
        ('PUnk11', UInt8),
        ('PUnk12', UInt8),
        ('PUnk13', UInt8),
        ('PUnk14', UInt8),
        ('PUnk15', UInt8),
    )
class MapInfo(Parser):
    structs = (
        ('Magic', Byte, 4),
        ('FileVersion', UInt32),
        ('Width', UInt32),
        ('Height', UInt32),
        ('Unknown2', UInt32),
        ('Unknown3', UInt32),
        ('Theme', String),
        ('Planet', String),
        ('BoundaryLeft', UInt32),
        ('BoundaryBottom', UInt32),
        ('BoundaryRight', UInt32),
        ('BoundaryTop', UInt32),
        ('Unknown4', UInt32),
        ('Unknown5', UInt32),
        ('LoaderImagePath', String),
        ('LoaderImageFormat', UInt32),
        ('Unknown6', UInt32),
        ('Unknown7', UInt32),
        ('Unknown8', UInt32),
        ('LoaderImageWidth', UInt32),
        ('LoaderImageHeight', UInt32),
        ('Unknown9', UInt32),
        ('Unknown10', UInt32),
        ('Players', List(Player, UInt8)),
    )

class MapParser(object):
    def __init__(self, filename):
        self.mpq = mpq.Archive(str(filename))
        self._info = {}

    @property
    def info(self):
        fp = StringIO(str(self.mpq['MapInfo']))
        p = MapInfo()
        data = p.serialize(fp)
        return data