import re
import logging

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

re_ip_in_phone = re.compile('000*-(\d+-\d+-\d+-\d+)')
re_phone_all_zero = re.compile('000*-0+-0+-0+-0+')
re_hostname = re.compile('[\w-]+\.[\w-]+')

fields = (
        'kw',
        'node',
        'name',
        'location',
        'sysop',
        'phone',
        'speed'
        )

metadata = None
engine = None
broker = None

Base = declarative_base()

class Flag(Base):
    __tablename__ = 'flags'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('nodes.id'))

    flag_name = Column(String)
    flag_val = Column(String)

class Raw(Base):
    __tablename__ = 'raw'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('nodes.id'))
    entry = Column(String)

class Node(Base):
    __tablename__ = 'nodes'

    transform = {
            'kw': lambda x: x.lower()
            }

    id = Column(Integer, primary_key=True)
    kw = Column(String, index=True)
    name = Column(String)
    location = Column(String)
    sysop = Column(String)
    phone = Column(String)
    speed = Column(String)

    zone = Column(Integer, index=True)
    region = Column(Integer, index=True)
    net = Column(Integer, index=True)
    node = Column(Integer)

    address = Column(String, index=True, unique=True)

    hub_id = Column(Integer, ForeignKey('nodes.id'))

    flags = relationship(Flag, backref='node')
    raw = relationship(Raw, backref='node')

    def __repr__ (self):
        return '<Node %s (%s)>' % (self.address, self.name)

    def __str__ (self):
        return self.__repr__()

    def inet(self, for_flag=None):
        '''Attempt to return the IP address or hostname for this
        node.  If you specify for_flag, look for a service specific address
        first.  Returns address or address:port if successful; returns None
        if unable to determine an address from the nodelist.'''

        ip = None
        port = None

        for flag in self.flags:
            # If there is an address attache to the requested flag,
            # prefer it over anything else.  Note that unlike
            # binkd_nodelister, we stop at the first instance
            # of the flag right now.
            if flag.flag_name == for_flag and flag.flag_val is not None:
                if '.' in flag.flag_val:
                    if ':' in flag.flag_val:
                        ip, port = flag.flag_val.split(':')
                    else:
                        ip = flag.flag_val
                    break
                else:
                    port = flag.flag_val

        if ip is None:
            # If the system name looks like an address, use it.
            mo = re_hostname.match(self.name)
            if mo:
                ip = self.name

        if ip is None:
            # Use address from IP or INA flags.
            for flag in self.flags:
                if flag.flag_name == 'IP' and flag.flag_val:
                    ip = flag.flag_val
                elif flag.flag_name == 'INA' and flag.flag_val:
                    ip = flag.flag_val

        if ip is None:
            # Extract IP address from phone number field.  This
            # is apparently a Thing That is Done, but I'm not
            # sure it's FTSC kosher.
            mo = re_ip_in_phone.match(self.phone)
            if mo and not re_phone_all_zero.match(self.phone):
                ip = mo.group(1).replace('-', '.')

        if ip is not None and ':' in ip:
            # Split an ip:port specification.
            ip = ip.split(':')[0]

        if ip:
            return port and '%s:%s' % (ip, port) or ip

    def to_nodelist(self):
        return ','.join([str(getattr(self, x)) for x in fields])

    def from_nodelist(self, line, addr):
        self.raw.append(Raw(entry=line))

        cols = line.rstrip().split(',')
        if len(cols) < len(fields):
            logging.debug('skipping invalid line: %s', line)
            return

        for k,v in (zip(fields, cols[:len(fields)])):
            if k in self.transform:
                v = self.transform[k](v)
            setattr(self, k, v)

        if self.kw == 'zone':
            logging.debug('start zone %s' % self.node)
            addr.zone = self.node
            addr.region = self.node
            addr.net = self.node
            addr.node = 0
        elif self.kw == 'region':
            logging.debug('start region %s' % self.node)
            addr.region = self.node
            addr.net = self.node
            addr.node = 0
        elif self.kw == 'host':
            logging.debug('start net %s' % self.node)
            addr.net = self.node
            addr.node = 0
        else:
            addr.node = self.node

        self.zone = addr.zone
        self.region = addr.region
        self.net = addr.net
        self.node = addr.node
        self.address = addr.ftn

        logging.debug('parsed node: %s' % self)

        flags = cols[len(fields):]

        for flag in flags:
            if ':' in flag:
                flag_name, flag_val = flag.split(':', 1)
            else:
                flag_name = flag
                flag_val = None

            self.flags.append(Flag(flag_name=flag_name, flag_val=flag_val))

class Nodelist (object):
    def __init__ (self, dburi):
        self.dburi = dburi

    def setup(self, create=False):
        self.metadata = Base.metadata
        self.engine = create_engine(self.dburi)

        if create:
            self.metadata.create_all(self.engine)

        self.broker = sessionmaker(bind=self.engine)

