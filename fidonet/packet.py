import os
import sys
import bitstring

from ftnerror import *
from util import *
from bitparser import Struct, Field, Container
from address import Address

class Packet (Container):

    origAddr = ftn_address_property('orig')
    destAddr = ftn_address_property('dest')

fts0001 = Struct(
            Field('origNode', 'uintle:16'),
            Field('destNode', 'uintle:16'),
            Field('year', 'uintle:16'),
            Field('month', 'uintle:16'),
            Field('day', 'uintle:16'),
            Field('hour', 'uintle:16'),
            Field('minute', 'uintle:16'),
            Field('second', 'uintle:16'),
            Field('baud', 'uintle:16'),
            Field('pktVersion', 'uintle:16', default=2),
            Field('origNet', 'uintle:16'),
            Field('destNet', 'uintle:16'),
            Field('productCodeLow', 'uintle:8'),
            Field('serialNo', 'uintle:8'),
            Field('password', 'bytes:8', default='\x00' * 8),
            Field('qOrigZone', 'uintle:16'),
            Field('qDestZone', 'uintle:16'),
            Field('fill', 'bytes:20'),
            Field('messages', 'bits'),

            factory=Packet
            )

fsc0048 = Struct(
            Field('origNode', 'uintle:16'),
            Field('destNode', 'uintle:16'),
            Field('year', 'uintle:16'),
            Field('month', 'uintle:16'),
            Field('day', 'uintle:16'),
            Field('hour', 'uintle:16'),
            Field('minute', 'uintle:16'),
            Field('second', 'uintle:16'),
            Field('baud', 'uintle:16'),
            Field('pktVersion', 'uintle:16', default=2),
            Field('origNet', 'uintle:16'),
            Field('destNet', 'uintle:16'),
            Field('productCodeLow', 'uintle:8'),
            Field('productRevMajor', 'uintle:8'),
            Field('password', 'bytes:8', default='\x00' * 8),
            Field('qOrigZone', 'uintle:16'),
            Field('qDestZone', 'uintle:16'),
            Field('auxNet', 'uintle:16'),
            Field('capWordValidationCopy', 'uintbe:16', default=1),
            Field('productCodeHigh', 'uintle:8'),
            Field('productRevMinor', 'uintle:8'),
            Field('capWord', 'uintle:16', default=1),
            Field('origZone', 'uintle:16'),
            Field('destZone', 'uintle:16'),
            Field('origPoint', 'uintle:16'),
            Field('destPoint', 'uintle:16'),
            Field('productData', 'uintle:32'),
            Field('messages', 'bits'),

            factory = Packet
            )

def PacketFactory(bits=None, fd=None):
    if bits is None:
        bits = bitstring.ConstBitStream(fd)

    pkt = fsc0048.parse(bits)

    # Heuristics from FSC-0048:
    # http://www.ftsc.org/docs/fsc-0048.002
    if pkt.pktVersion != 2:
        raise InvalidPacket()

    if pkt.capWord != pkt.capWordValidationCopy \
            or pkt.capWord == 0 \
            or pkt.capWord & 0x01 == 0:
        bits.pos = 0
        pkt = fts0001.parse(bits)

    return pkt

if __name__ == '__main__':
    p = PacketFactory(fd=open(sys.argv[1]))

    print '=' * 70
    print '%(origZone)s:%(origNet)s/%(origNode)s ->' % p,
    print '%(destZone)s:%(destNet)s/%(destNode)s' % p,
    print '@ %(year)s-%(month)s-%(day)s %(hour)s:%(minute)s:%(second)s' % p
    print '=' * 70
    print

