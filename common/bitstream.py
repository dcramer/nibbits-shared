class BitStream(object):
    def __init__(self, buf='', debug=False):
        self.buf = [ord(x) for x in buf]

        self.pos = 0
        self.len = len(buf)*8
        
        self.debug = debug

        self.closed = False
        self.softspace = 0

    def close(self):
        if not self.closed:
            self.closed = True
            del self.buf, self.pos, self.len, self.softspace

    def isatty(self):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        return 0

    def seekbits(self, pos, mode=0):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        if mode == 1:
            pos += self.pos
        elif mode == 2:
            pos += self.len
        self.pos = max(0, pos)
    
    def seek(self, pos, mode=0):
        return self.seekbits(pos*8, mode)

    def tell(self):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        return self.pos

    def flush(self):
        if self.closed:
            raise ValueError, "I/O operation on closed file"

    def truncate(self, size=None):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        if size is None:
            size = self.pos
        elif size < 0:
            raise IOError(EINVAL, "Negative size not allowed")
        elif size < self.pos:
            self.pos = size

        self.len = size
        self.buf = self.buf[:(size//8)+(size%8 != 0)]
        if self.buf != []:
            self.buf[-1] = self.buf[-1] & (1<<(size%8))-1
        
    def writebits(self, n, bitlen):
        """Writes bits"""
        
        if self.closed:
            raise ValueError, "I/O operation on closed file"

        n &= (1L << bitlen)-1

        newpos = self.pos + bitlen

        startBPos = self.pos%8
        startBlock = self.pos//8

        endBPos = newpos%8
        endBlock = newpos//8+(endBPos != 0)

        while len(self.buf) < endBlock: self.buf += [0]

        pos = startBPos

        while bitlen > 0:
            bitsLeft=8-(pos%8)
            if bitsLeft > bitlen: bitsLeft=bitlen
            
            mask=(1<<bitsLeft)-1

            self.buf[startBlock+(pos//8)] ^= self.buf[startBlock+(pos//8)]&(mask<<(pos%8))
            self.buf[startBlock+(pos//8)] |= int(n&mask)<<(pos%8)
        
            n >>= bitsLeft
            bitlen -= bitsLeft
            
            pos+=bitsLeft

        self.pos = newpos
        if self.pos > self.len:
            self.len = self.pos

    def align(self):
        """Aligns to the next byte to the right"""
        address, offset = divmod(self.tell(), 8)
        if offset:
            self.seekbits(8 - offset, 1)
        if self.debug:
            print "align"

    def readbits(self, bitlen):
        """Reads bits"""
        
        if self.closed:
            raise ValueError, "I/O operation on closed file"

        obitlen = bitlen

        newpos = self.pos + bitlen

        startBPos = self.pos%8
        startBlock = self.pos//8

        endBPos = newpos%8
        endBlock = newpos//8+(endBPos != 0)

        ret=0

        pos = startBPos
        shift = 0

        while bitlen > 0:
            bitsLeft=8-(pos%8)
            if bitsLeft > bitlen: bitsLeft=bitlen

            mask = (1<<bitsLeft)-1

            ret |= long((self.buf[startBlock+(pos//8)] >> (pos%8)) & mask) << shift

            shift += bitsLeft

            bitlen -= bitsLeft
            pos += bitsLeft

        self.pos = newpos

        if self.debug:
            print "%s bits = %s" % (obitlen, ret)

        return ret

    def getvalue(self):
        """Get the buffer"""
        
        return ''.join(map(chr, self.buf))

    def write(self, s):
        for c in str(s):
            self.writebits(ord(c), 8)

    def read(self, i):
        self.align()
        
        startBlock = self.pos//8
        endBlock = startBlock + i
        
        outval = ''.join(chr(i) for i in self.buf[startBlock:endBlock])
        
        if self.debug:
            print "%s bytes = %s" % (i, outval)
        
        self.pos += 8 * i
        
        return outval