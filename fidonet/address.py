from ftnerror import *
import re

re_ftn_addr = re.compile('''
        ((?P<zone>\d+):)?
        (?P<net>\d+)/
        (?P<node>\d+)
        (.(?P<point>\d+))?
        (@(?P<domain>\w+))?
        ''', re.VERBOSE)

re_rfc_addr = re.compile('''
        (p(?P<point>\d+)\.)?
        f(?P<node>\d+)\.
        n(?P<net>\d+)\.
        z(?P<zone>\d+)\.
        fidonet.org
        ''', re.VERBOSE)

def int_property(name):
    '''Create a class property that converts all values to ints.'''

    def s(self, v):
        if v is not None:
            setattr(self, '_%s' % name, int(v))

    def g(self):
        return getattr(self, '_%s' % name)

    return property(g,s)

class Address (object):
    '''A class for parsing and creating FTN network addresses.

    Parsing
    -------

    The class will parse both RFC and FTN style representations.  For
    example::

      >>> a = Address('1:322/761')
      >>> a.ftn
      '1:322/761'
      >>> a.rfc
      'f761.n322.z1.fidonet.org'

      >>> a = Address('f761.n322.z1.fidonet.org')
      >>> a.ftn
      '1:322/761'

    Creating
    --------

    You can also create addresses::

      >>> a = Address(zone=1, node=761, net=322)
      >>> a.ftn
      '1:322/761'

    An empty address has node=0 and net=0 and all other fields unset::

      >>> a = Address()
      >>> a.ftn
      '0/0'
      >>> a.zone = 1
      >>> a.ftn
      '1:0/0'

    '''

    fields = [ 'zone', 'net', 'node', 'point' ]

    def __init__ (self,
            addr=None,
            rfc_domain='fidonet.org',
            ftn_domain='fidonet',
            ftn5d=False,
            **kw):

        self.rfc_domain = rfc_domain
        self.ftn_domain = ftn_domain
        self.ftn5d = ftn5d

        # defaults
        self._zone = 0
        self._net = 0
        self._node = 0
        self._point = 0

        for k,v in kw.items():
            if k in self.fields:
                setattr(self, k, v)

        if isinstance(addr, Address):
            self._zone = addr.zone
            self._net = addr.net
            self._node = addr.node
            self._point = addr.point
        elif addr is not None:
            self.parse_from_string(addr)

    def parse_from_string(self, addr):
            for x in [ re_ftn_addr, re_rfc_addr ]:
                mo = x.match(addr)
                if mo:
                    for k in self.fields:
                        if mo.groupdict().get(k) is not None:
                            setattr(self, k, mo.group(k))
                    return

            raise InvalidAddress(addr)

    zone = int_property('zone')
    net = int_property('net')
    node = int_property('node')
    point = int_property('point')

    def _ftn(self, showPoint=True):
        addr = []
        if self.get('zone', 0) > 0:
            addr.append('%(zone)s:' % self)

        addr.append('%(net)s/%(node)s' % self)

        if showPoint and self.get('point', 0) > 0:
            addr.append('.%(point)s' % self)

        if self.ftn5d:
            addr.append('@%s' % self.ftn_domain)

        return ''.join(addr)

    def _pointless(self):
        return self._ftn(showPoint=False)

    def _msg(self):
        return '%(net)s/%(node)s' % self

    def _rfc(self, showPoint=True):
        addr = []

        for field in [ 'zone', 'net', 'node']:
            if self.get(field) is None:
                raise InvalidAddress()

        if showPoint and self.get('point', 0) > 0:
            addr.append('p%(point)s' % self)

        addr.append('f%(node)s.n%(net)s.z%(zone)s' % self)
        addr.append(self.rfc_domain)

        return '.'.join(addr)

    def _hex(self):
        return '%(net)04x%(node)04x' % self

    ftn = property(_ftn)
    pointless = property(_pointless)
    rfc = property(_rfc)
    hex = property(_hex)
    msg = property(_msg)

    def __str__(self):
        return self.ftn

    def __repr__ (self):
        return self.__str__()

    def __getitem__(self, k):
        if k in self.fields:
            return getattr(self, k)
        else:
            raise KeyError(k)

    def get(self, k, default=None):
        try:
            return getattr(self, k, None)
        except AttributeError:
            return default

if __name__ == '__main__':
    a = Address('1:322/761')
    b = Address('f761.n322.z1.fidonet.org')

