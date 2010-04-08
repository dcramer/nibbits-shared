"""
Parses out SC2Replay files.

>>> from common.parsers.replays import ReplayInfo
>>> from common.bitstream import BitStream
>>> 
>>> fp = BitStream(open('Path.SC2Replay', 'rb'))
>>> parser = ReplayInfo()
>>> data = parser.serialize(fp)
>>> print "Map filename: ", data.GameInfo.MapInfo.CachePath

You can also test w/ this file directly:

``python replays.py <filepath.sc2replay>``

"""
from common.bitstream import BitStream
from common.parser import Parser

import mpq

class AsciiString(Parser):
    def serialize(self, fp, length, min_value=None, max_value=None, **kwargs):
        value = fp.readbits(length) >> 3
        if min_value:
            assert value >= min_value, "exceeded min value of %s (was %s)" % (min_value, value)
        if max_value:
            assert value <= max_value, "exceeded max value of %s (was %s)" % (max_value, value)
        return fp.read(value)

UnicodeString = AsciiString

class Integer(Parser):
    def serialize(self, fp, length, min_value=None, max_value=None, **kwargs):
        value = fp.readbits(length)
        if min_value:
            assert value >= min_value, "exceeded min value of %s (was %s)" % (min_value, value)
        if max_value:
            assert value <= max_value, "exceeded max value of %s (was %s)" % (max_value, value)
        return value

class Boolean(Parser):
    def serialize(self, fp, **kwargs):
        return bool(fp.readbits(1))

class Byte(Parser):
    def serialize(self, fp, length, min_value=None, max_value=None, **kwargs):
        value = fp.readbits(length)
        if min_value:
            assert value >= min_value, "exceeded min value of %s (was %s)" % (min_value, value)
        if max_value:
            assert value <= max_value, "exceeded max value of %s (was %s)" % (max_value, value)
        return value

class List(Parser):
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

class Nullable(Parser):
    def __init__(self, type=Byte):
        self.type = type
        
    def serialize(self, fp, length, **kwargs):
        present = fp.readbits(1)
        if present:
            return self.type().serialize(fp, length, **kwargs)

class Enum(Parser):
    choices = []
    
    def __init__(self, *choices):
        self.choices = choices
        
    def serialize(self, fp, length, min_value=None, max_value=None, **kwargs):
        value = fp.readbits(length)
        if min_value:
            assert value >= min_value, "exceeded min value of %s (was %s)" % (min_value, value)
        if max_value:
            assert value <= max_value, "exceeded max value of %s (was %s)" % (max_value, value)
        return self.choices[value]


class FixedString(Parser):
    # Length is in bytes
    def serialize(self, fp, length, **kwargs):
        return fp.read(length)

class Hash(Parser):
    def serialize(self, fp, length, **kwargs):
        return binascii.hexlify(fp.read(length))

class Client(Parser):
    structs = (
        ('Name', UnicodeString, 8, 0, 32),
        ('Unknown049', Integer, 32, 0, 4294967295),
        ('Unknown04A', Nullable, 8, 0, 254),
        ('Unknown04B', Boolean),
        ('Unknown04C', Boolean),
        ('Unknown04D', Enum('Unknown0', 'Unknown1', 'Unknown2'), 2, 0, 2),
    )

class Unknown1A1(Parser):
    structs = (
        ('Unknown1A2', Boolean),
        ('Unknown1A3', Boolean),
        ('Unknown1A4', Boolean),
        ('Unknown1A5', Boolean),
        ('Unknown1A6', Boolean),
        ('Unknown1A7', Boolean),
        ('Unknown1A8', Boolean),
        ('Unknown1A9', Enum('Unknown0', 'Unknown1', 'Unknown2', 'Unknown3', 'Unknown4'), 3),
        ('Unknown1AA', Enum('Unknown0', 'Unknown1', 'Unknown2', 'Unknown3'), 2),
        ('Unknown1AB', Enum('Unknown0', 'Unknown1', 'Unknown2', 'Unknown3'), 2),
        ('Unknown1AC', Enum('Unknown0', 'Unknown1', 'Unknown2', 'Unknown3'), 2),
    )

class NeededFile(Parser):
    structs = (
        ('Type', FixedString, 4),
        ('Unknown', Byte, 4),
        ('Locale', FixedString, 3),
        ('Hash', Hash, 32),
    )

class Unknown1B1(Parser):
    structs = (
        P('Unknown1B2', List(Boolean), 6, 0, 32),
        P('Unknown1B3', List(Boolean), 8, 0, 255),
        P('Unknown1B4', List(Boolean), 6, 0, 32),
        P('Unknown1B5', List(Boolean), 8, 0, 255),
        P('Unknown1B6', List(Boolean), 2, 0, 3),
    )

class MapInfo(Parser):
    structs = (
        ('Unknown1BF', Integer, 32, 0, 4294967295),
        ('Unknown1C0', UnicodeString, 10, 0, 255),
        ('Unknown1C1', Unknown1A1),
        ('Unknown1C2', Enum('Unknown0', 'Unknown1', 'Unknown2', 'Unknown3', 'Unknown4'), 3, 0, 4),
        ('Unknown1C3', Enum('Unknown0', 'Unknown1', 'Unknown2', 'Unknown3', 'Unknown4', 'Unknown5', 'Unknown6'), 3, 0, 6),
        ('Unknown1C4', Byte, 5, 0, 16),
        ('Unknown1C5', Byte, 5, 0, 16),
        ('Unknown1C6', Byte, 4, 0, 15),
        ('Unknown1C7', Byte, 4, 1, 16),
        ('Unknown1C8', Byte, 5, 1, 32),
        ('Unknown1C9', Byte, 8, 1, 255),
        ('Unknown1CA', Byte, 8, 1, 255),
        ('Unknown1CB', Byte, 8, 0, 255),
        ('Unknown1CC', Byte, 8, 0, 255),
        ('Unknown1CD', Integer, 32, 0, 4294967295),
        ('CachePath', UnicodeString, 10, 0, 128),
        ('Unknown1CF', Integer, 32, 0, 4294967295),
        ('Unknown1D0', UnicodeString, 10, 0, 128),
        ('Unknown1D1', List(Unknown1B1), 5, 0, 16),
        ('Unknown1D2', Byte, 6, 0, 32),
        ('NeededFiles', List(NeededFile), 4, 0, 10),
    )

class PlayerSetup(Parser):
    structs = (
        ('Unknown1D7', Byte, 8),
        ('Unknown1D8', Nullable, 4),
        ('Unknown1D9', Byte, 4),
        ('Unknown1DA', Nullable, 5),
        ('Unknown1DB', Nullable, 8),
        ('Unknown1DC', Byte, 6),
        ('Unknown1DD', Byte, 7),
        ('Unknown1DE', Enum('Unknown0', 'Unknown1', 'Unknown2'), 2),
    )

class Unknown1E2(Parser):
    structs = (
        ('Unknown1E3', Enum('Unknown0', 'Unknown1', 'Unknown2', 'Unknown3', 'Unknown4', 'Unknown5'), 3),
        ('Unknown1E4', Byte, 5),
        ('Unknown1E5', Byte, 5),
        ('PlayerSetups', List(PlayerSetup), 5),
        ('Unknown1E7', Integer, 32),
        ('Unknown1E8', Nullable, 4),
        ('Unknown1E9', Boolean),
        ('Unknown1EA', Integer, 32),
        ('Unknown1EB', Byte, 6),
    )

class GameInfo(Parser):
    structs = (
        ('Clients', List(Client), 5, 0, 16),
        ('MapInfo', MapInfo),
        ('Unknown1E2', Unknown1E2),
    )

class Player(Parser):
    structs = (
        ('Name', UnicodeString, 8),
        ('Race', UnicodeString, 8),
        ('Color', UnicodeString, 7),
    )

class ReplayInfo(Parser):
    structs = (
        ('GameInfo', GameInfo),
        ('MapTitle', UnicodeString, 10, 0, 255),
        ('Unknown22D', UnicodeString, 8, 0, 63),
        ('Players', List(Player), 5, 0, 16),
    )

class ReplayParser(object):
    def __init__(self, filename):
        self.mpq = mpq.Archive(str(filename))
        self._info = {}

    @property
    def info(self):
        fp = BitStream(str(self.mpq['replay.info']), debug=True)
        p = ReplayInfo()
        return p.serialize(fp)