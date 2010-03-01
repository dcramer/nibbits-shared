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

import mpq

from common.bitstream import BitStream
from common.bitparser import *

class Client(BitParser):
    structs = (
        ('Name', UnicodeString, 8),
        ('Unknown049', Integer, 32),
        ('Unknown04A', Nullable, 8),
        ('Unknown04B', Boolean),
        ('Unknown04C', Boolean),
        ('Unknown04D', Enum('Unknown0', 'Unknown1', 'Unknown2'), 2),
    )

class Unknown1A1(BitParser):
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

class NeededFile(BitParser):
    structs = (
        ('Type', FixedString, 4),
        ('Unknown', Byte, 4),
        ('Locale', FixedString, 3),
        ('Hash', Hash, 32),
    )

class Unknown1B1(BitParser):
    structs = (
        P('Unknown1B2', List(Boolean), 6, 0, 32),
        P('Unknown1B3', List(Boolean), 8, 0, 255),
        P('Unknown1B4', List(Boolean), 6, 0, 32),
        P('Unknown1B5', List(Boolean), 8, 0, 255),
        P('Unknown1B6', List(Boolean), 2, 0, 3),
    )

class MapInfo(BitParser):
    structs = (
        ('Unknown1BF', Integer, 32),
        ('Unknown1C0', UnicodeString, 10),
        ('Unknown1C1', Unknown1A1),
        ('Unknown1C2', Enum('Unknown0', 'Unknown1', 'Unknown2', 'Unknown3', 'Unknown4'), 3),
        ('Unknown1C3', Enum('Unknown0', 'Unknown1', 'Unknown2', 'Unknown3', 'Unknown4', 'Unknown5', 'Unknown6'), 3),
        ('Unknown1C4', Byte, 5),
        ('Unknown1C5', Byte, 5),
        ('Unknown1C6', Byte, 4),
        ('Unknown1C7', Byte, 4),
        ('Unknown1C8', Byte, 5),
        ('Unknown1C9', Byte, 8),
        ('Unknown1CA', Byte, 8),
        ('Unknown1CB', Byte, 8),
        ('Unknown1CC', Byte, 8),
        ('Unknown1CD', Integer, 32),
        ('CachePath', UnicodeString, 10),
        ('Unknown1CF', Integer, 32),
        ('Unknown1D0', UnicodeString, 10),
        ('Unknown1D1', List(Unknown1B1), 5, 0, 16),
        ('Unknown1D2', Byte, 6, 0, 32),
        ('NeededFiles', List(NeededFile), 4),
    )

class PlayerSetup(BitParser):
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

class Unknown1E2(BitParser):
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

class GameInfo(BitParser):
    structs = (
        ('Clients', List(Client), 5),
        ('MapInfo', MapInfo),
        ('Unknown1E2', Unknown1E2),
    )

class Player(BitParser):
    structs = (
        ('Name', UnicodeString, 8),
        ('Race', UnicodeString, 8),
        ('Color', UnicodeString, 7),
    )

class ReplayInfo(BitParser):
    structs = (
        ('GameInfo', GameInfo),
        ('MapTitle', UnicodeString, 10),
        ('Unknown22D', UnicodeString, 8),
        ('Players', List(Player), 5),
    )

class SC2Replay(object):
    def __init__(self, filepath):
        self.mpq = mpq.Archive(str(filepath))

    @property
    def info(self):
        parser = ReplayInfo()
        value = parser.serialize(BitStream(str(self.mpq['replay.info'])))
        setattr(self, 'info', value)
        return value

if __name__ == '__main__':
    parser = SC2Replay(' '.join(sys.argv[2:]))
    data = parser.info
    print "Map filename: ", data.GameInfo.MapInfo.CachePath