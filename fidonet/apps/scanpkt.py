#!/usr/bin/python

import os
import sys

import fidonet
import fidonet.app

class App (fidonet.app.App):
    logtag = 'fidonet.scanpkt'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-m', '--show-messages', action='store_true')
        p.add_option('-t', '--show-message-text', action='store_true')

        return p

    def handle_args(self, args):
        self.for_each_arg(self.scan_pkt, args)

    def scan_pkt(self, src, name, ctx):
        pkt = fidonet.PacketFactory(src)

        print '=' * 70
        print '%s: ' % name,
        print pkt
        print '=' * 70
        print

        if self.opts.show_messages:
            for i, msg in enumerate(pkt.messages):
                print '[%03d]' % i
                print msg
                print

                if self.opts.show_message_text:
                    print msg.body
                    print

if __name__ == '__main__':
    App.run()

