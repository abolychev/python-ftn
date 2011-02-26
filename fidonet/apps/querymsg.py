#!/usr/bin/python

import os
import sys

import fidonet
import fidonet.app

class App (fidonet.app.App):
    logtag = 'fidonet.querymsg'

    def create_parser(self):
        p = super(App, self).create_parser()
        p.add_option('-q', '--query', action='append', default=[])
        p.add_option('--queryformat', '--qf')
        return p

    def query_msg(self, fd, name):
        msg = fidonet.MessageFactory(fd)
        
        try:
            if self.opts.queryformat:
                print self.opts.queryformat % msg
            else:
                for k in self.opts.query:
                    print msg[k]
        except KeyError, detail:
            print >>sys.stderr, 'error: %s: no such field.' % detail

    def handle_args(self, args):
        if args:
            for msgfile in args:
                self.query_msg(open(msgfile), msgfile)
        else:
            self.query_msg(sys.stdin, '<stdin>')

if __name__ == '__main__':
    App.run()
