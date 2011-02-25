import os
import sys
import bitstring
from StringIO import StringIO

from ftnerror import *
from util import *
from bitparser import Container
import odict

from formats import packedmessage, diskmessage, attributeword

class Message (Container):
    def _setAW (self, aw):
        self['attributeWord'] = attributeword.AttributeWordParser.build(aw)

    def _getAW (self):
        self['attributeWord'].pos = 0
        return attributeword.AttributeWordParser.parse(self['attributeWord'])

    attributeWord = property(_getAW, _setAW)

    def _getBody (self):
        return MessageBodyParser.parse(self['body'])

    def _setBody (self, body):
        self['body'] = MessageBodyParser.build(body)

    body = property(_getBody, _setBody)

    origAddr = ftn_address_property('orig')
    destAddr = ftn_address_property('dest')

class MessageBody (Container):
    def render(self):
        return self.build(self)\
                .replace('\r', '\n')\
                .replace('\x01', '[K]')

# Everything below this is an ungodly mess.  Why, Fidonet, why!?

class _MessageBodyParser (object):
    kludgePrefix = '\x01'

    def create(self):
        body = MessageBody(self, {
            'area': None,
            'origin': None,
            'klines': odict.odict(),
            'seenby': [],
            'body': '',
            })

        body.__struct__ = self

        return body

    def parse(self, raw):
        msg = self.create()

        state = 0
        body = []

        for line in raw.split('\r'):
            if state == 0:
                state = 1

                if line.startswith('AREA:'):
                    msg['area'] = line.split(':', 1)[1]
                    continue

            if state == 1:
                if line.startswith('\x01'):
                    self.addKludge(msg, line)
                elif line.startswith(' * Origin:'):
                    msg['origin'] = line
                    state = 2
                else:
                    body.append(line)
            elif state == 2:
                if line.startswith('\x01'):
                    self.addKludge(msg, line)
                elif line.startswith('SEEN-BY:'):
                    msg['seenby'].append(line.split(': ', 1)[1])
                elif len(line) == 0:
                    pass
                else:
                    raise ValueError('Unexpected: %s'    % line)

        msg['body'] = '\n'.join(body)

        return msg

    def build(self, msg):
        lines = []

        if msg['area']:
            lines.append('AREA:%(area)s' % msg)

        for k,vv in msg['klines'].items():
            for v in vv:
                lines.append('%s%s %s' % (self.kludgePrefix, k,v))

        lines.extend(msg['body'].split('\n'))

        if msg['origin']:
            lines.append(msg['origin'])

        for seenby in msg['seenby']:
            lines.append('SEEN-BY: %s' % seenby)

        return '\r'.join(lines)

    def addKludge(self, msg, line):
        k,v = line[1:].split(None, 1)

        if k in msg['klines']:
            msg['klines'][k].append(v)
        else:
            msg['klines'][k] = [v]

MessageBodyParser = _MessageBodyParser()
MessageParser = packedmessage.MessageParser

def MessageFactory(bits=None, fd=None):
    if bits is None:
        bits = bitstring.ConstBitStream(fd)

    msg = packedmessage.MessageParser.parse(bits, Message)
    if msg.msgVersion != 2:
        bits.pos = 0
        msg = diskmessage.MessageParser.parse(bits, Message)

    return msg

if __name__ == '__main__':
    m = MessageFactory(fd=open(sys.argv[1]))

