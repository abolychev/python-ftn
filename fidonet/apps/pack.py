import os
import sys
import time

from fidonet import Address, MessageFactory
from fidonet.formats import *
import fidonet.app

class App(fidonet.app.App):
    logtag = 'fidonet.pack'

    def create_parser(self):
        p = super(App, self).create_parser()

        p.add_option('--output', '--out')
        p.add_option('-o', '--origin', '--orig')
        p.add_option('-d', '--destination', '--dest')

        return p

    def handle_args (self, args):
        if not self.opts.origin:
            try:
                self.opts.origin = self.cfg.get('fidonet', 'address')
            except Exception, detail:
                self.log.error('Missing origin address.')
                sys.exit(1)

        if not self.opts.destination:
            self.log.error('Missing destination address.')
            sys.exit(1)

        pkt = fsc0048packet.PacketParser.create()

        pkt.origAddr = Address(self.opts.origin)
        pkt.destAddr = Address(self.opts.destination)
        pkt.time = time.localtime()

        count = 0
        for msgfile in args:
            msg = MessageFactory(open(msgfile))
            pkt.messages.append(packedmessage.MessageParser.build(msg))
            count += 1
            self.log.info('packed message from %s @ %s to %s @ %s' %
                    (msg.fromUsername, msg.origAddr, msg.toUsername,
                        msg.destAddr))

        if self.opts.output:
            sys.stdout = open(self.opts.output, 'w')
        else:
            self.opts.output = '<stdout>'

        pkt.write(sys.stdout)
        self.log.info('packed %d messages into %s.' % (count,
            self.opts.output))

if __name__ == '__main__':
    App.run()

