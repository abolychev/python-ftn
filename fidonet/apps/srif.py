import os
import sys
import subprocess
import tempfile
from stat import *

import fidonet.srif
import fidonet.app

class App (fidonet.app.App):
    def create_parser (self):
        p = super(App, self).create_parser()
        p.add_option('-D', '--basedir')
        p.add_option('-M', '--magicdir')
        return p

    def set_defaults (self):
        super(App, self).set_defaults()

        if not self.cfg.has_section('binkd'):
            self.cfg.add_section('binkd')

        self.cfg.set('DEFAULT', 'files',
                os.path.join(self.opts.data_dir, 'files'))

    def handle_args (self, args):
        if self.opts.basedir is None:
            self.opts.basedir = self.get_data_path('binkd', 'files')

        if self.opts.magicdir is None:
            self.opts.magicdir = self.get_data_path('binkd', 'magic')

        if self.opts.basedir is None:
            self.log.error('base directory is not set')
            sys.exit(1)

        if not os.path.isdir(self.opts.basedir):
            self.log.error('base directory "%s" does not exist' %
                    self.opts.basedir)
            sys.exit(1)

        self.log.debug('basedir = %s' % self.opts.basedir)

        self.process_srif(args)

    def process_srif(self, args):
        if args:
            sys.stdin = open(args.pop(0))

        data = fidonet.srif.SRIF(sys.stdin)

        req = open(data['RequestList'])
        rsp = open(data['ResponseList'], 'r+')
        rsp.truncate()

        for line in (x.strip() for x in req):
            if not line:
                continue

            if line.startswith('/'):
                self.log.warn('ignoring absolute path: %s' % line)
                continue

            if '..' in line:
                self.log.warn('ignoring path containing "..": %s' % line)
                continue

            # First check for magic file matching request.
            if self.opts.magicdir:
                reqpath = os.path.join(self.opts.magicdir, line)
                if self.is_exe_file(reqpath):
                    self.log.info('request for magic file: %s' % line)
                    tmppath = self.run_magic_file(reqpath)
                    print >>rsp, '-%s' % tmppath
                    continue

            reqpath = os.path.join(self.opts.basedir, line)

            if not os.path.isfile(reqpath):
                self.log.warn('request for invalid file: %s' % line)
                continue
            else:
                self.log.info('request for normal file: %s' % line)
                print >>rsp, '+%s' % reqpath

    def run_magic_file(self, path):
        tmpfd, tmpname = tempfile.mkstemp()
        tmpfd = os.fdopen(tmpfd)

        rc = subprocess.call([path, self.opts.basedir], stdout=tmpfd)

        if rc != 0:
            self.log.error('request for magic file failed, rc = %d' % rc)
            tmpfd.seek(0)
            print >>tmpfd, 'File request failed.'
            tmpfd.truncate()

        return tmpname

    def is_exe_file(self, path):
        return os.path.isfile(path) and \
            os.stat(path)[ST_MODE] & (S_IXUSR|S_IXGRP|S_IXOTH)

if __name__ == '__main__':
    App.run()

