import array

class BitStream(object):
    _bytesperlong = 32/len(array.array('L',32*' '))
    _bitsperlong = _bytesperlong*8

    def __init__(self, source_str):
        self._totalbits = len(source_str) * 8
        self._position = 0

        # Pad to longword boundary, then make an array

        source_str += -len(source_str) % self._bytesperlong * chr(0)
        self._bitstream = array.array('L', source_str)

    def seek(self, offset, whence=0):
        self._position = offset + (0, self._position, self._totalbits)[whence]

    def tell(self):
        return self._position

    def align(self):
        address, offset = divmod(self._position, 8)
        if offset:
            self.seek(8 - offset, 1)

    def read(self, length):
        self.align()

        longaddress = self._position / self._bitsperlong
        endaddress = (self._position + length) / self._bitsperlong

        outval = self._bitstream[longaddress:endaddress]

        self._position += length * 8

        return outval

    def readbits(self, length):
        bitsperlong, position = self._bitsperlong, self._position
        
        if position < 0 or position + length > self._totalbits:
            raise IndexError, "Invalid bitarray._position/length"

        longaddress, bitoffset = divmod(position, bitsperlong)

        # We may read bits in the final word after ones we care
        # about, so create a mask to remove them later.

        finalmask = (1L << length) - 1

        # We may read bits in the first word before the ones we
        # care about, so bump the total bits to read by this
        # amount, so we read enough higher-order bits.

        length += bitoffset

        # Read and concatenate every long which contains a bit we need

        outval,outshift = 0L,0
        while length > 0:
            outval += self._bitstream[longaddress] << outshift
            longaddress += 1
            outshift += bitsperlong
            length -= bitsperlong

        # length is now basically a negative number which tells us
        # how many bits to back up from our current position.

        self._position = longaddress*bitsperlong + length

        # Shift right to strip off the low-order bits we
        # don't want, then 'and' with the mask to strip
        # off the high-order bits we don't want.

        return (outval >> bitoffset) & finalmask
