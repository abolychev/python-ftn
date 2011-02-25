#!/usr/bin/python

import os
import sys
import time

import fidonet
import fidonet.app
import fidonet.message

class App (fidonet.app.App):
    logtag = 'fidonet.editpkt'

    def create_parser(self):
        p = super(App, self).create_parser()

        p.add_option('-o', '--origin', '--orig')
        p.add_option('-d', '--destination', '--dest')
        p.add_option('-t', '--time',
                help='Set the time in the packet, specified as "YYYY-mm-dd HH:MM:SS"')
        p.add_option('--capword')
        p.add_option('--productdata')

        return p

    def handle_args(self, args):

        for pktfile in args:
            self.log.info('Editing %s.' % pktfile)
            fd = open(pktfile, 'r+')
            pkt = fidonet.PacketFactory(fd=fd)

            if self.opts.origin:
                pkt.origAddr = fidonet.Address(self.opts.origin)
                self.log.debug('set origAddr = %s' % pkt.origAddr)
            if self.opts.destination:
                pkt.destAddr = fidonet.Address(self.opts.destination)
                self.log.debug('set destAddr = %s' % pkt.destAddr)
            if self.opts.time:
                t = time.strptime(self.opts.time, '%Y-%m-%d %H:%M:%S')
                pkt.time = t
                self.log.debug('set time = %s' % time.strftime(
                    '%Y-%m-%d %H:%M:%S', t))
            if self.opts.capword:
                pkt.capWord = int(self.opts.capword)
                self.log.debug('set capword = %d' % pkt.capWord)

            fd.seek(0)
            fidonet.packet.PacketParser.write(pkt, fd)
            fd.close()

if __name__ == '__main__':
    App.run()

