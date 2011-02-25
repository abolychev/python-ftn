'''This is the basic Fidonet packet structure defined in FTS-0001_.  This
format appears to have been largely superceded by the type 2+ packet
format.

.. _FTS-0001: http://www.ftsc.org/docs/fts-0001.016
'''

from fidonet.bitparser import Struct, Field, CString, BitStream
from fidonet.util import fixup_packet
from fidonet.packet import Packet

PacketParser = Struct(
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
            Field('productCodeLow', 'uintle:8', default=0xFE),
            Field('serialNo', 'uintle:8'),
            Field('password', 'bytes:8', default='\x00' * 8),
            Field('origZone', 'uintle:16'),
            Field('destZone', 'uintle:16'),
            Field('fill', 'bytes:20'),
            BitStream('messages'),

            validate=fixup_packet,
            factory=Packet
            )

