import struct
from InotifyReactor.Libc import libc
from InotifyReactor.Utils import splitMask
from InotifyReactor.InotifyFlags import *

class Inotify:
  """ ctypes wrapper for inotify system calls, manages watch descriptors using
      path as key """

  def __init__(self, *args, **kwargs):
    flags = kwargs['flags'] if 'flags' in kwargs else 0
    fd = libc.inotify_init1(flags)

    if -1 == fd:
      raise Inotify.Error("Error in inotify_init1()")

    self.event_descriptor = fd
    self.watch_descriptors = {}

  def add_watch(self, pathname, mask):
    wd = libc.inotify_add_watch(self.event_descriptor, pathname, mask)

    if -1 == wd:
      raise Inotify.Error("Error in inotify_add_watch()")

    if pathname not in self.watch_descriptors:
      self.watch_descriptors[pathname] = Inotify.Watch(pathname, 0, wd)

    self.watch_descriptors[pathname].mask |= mask

  def remove_watch(self, pathname):
    if pathname not in self.watch_descriptors:
      raise Inotify.Error("Path not in current watch set")

    result = libc.inotify_rm_watch(self.event_descriptor,
      self.watch_descriptors[pathname])

    if -1 == result:
      raise Inotify.Error("Error in inotify_rm_watch()")

    del(self.watch_descriptors[pathname])

  def __iter__(self):
    for k,v in self.watch_descriptors.iteritems():
      yield v

  class EventMask:

    def __init__(self, mask):
      self.mask = mask

    def __str__(self):
      return '(' + ' | '.join(splitMask(self.mask, IN_FLAG_NAMES)) + ')'

  class Watch:

    def __init__(self, pathname, mask, wd):
      self.pathname = pathname
      self.mask = mask
      self.wd = wd

    def __str__(self):
      return (
        '{{\n'
        '  Inotify.Watch: \n'
        '   pathname: {0}\n'
        '   mask: {1}\n'
        '   wd: {2}\n'
        '}}\n'
      ).format(
        self.pathname,
        self.mask,
        self.wd
      )

  class Error(Exception):

    def __init__(self, message, errors = None):
      super(Inotify.Error, self).__init__(message)
      self.errors = errors

  class Event:
    Format = '<iIII'
    HeaderSize = struct.calcsize(Format)

    def __init__(self, wd, mask, cookie, name):
      self.wd = wd
      self.mask = mask
      self.cookie = cookie
      self.name = name
      self.len = len(name)
      self.size = Inotify.Event.HeaderSize + self.len

    @classmethod
    def deserialize(self, data):
      if len(data) <= Inotify.Event.HeaderSize:
        raise Inotify.Error("Invalid header size")

      [wd, mask, cookie, length] =\
        struct.unpack_from(Inotify.Event.Format, data)

      if len(data) < Inotify.Event.HeaderSize + length:
        raise Inotify.Error

      name = ''.join([b.decode('utf-8') for b in struct.unpack_from(
        length * 'c',
        data,
        Inotify.Event.HeaderSize)])

      return Inotify.Event(wd, mask, cookie, name)

    def __str__(self):

      try:
        padding = len(self.name) - self.name.index(chr(0))
      except ValueError as e:
        padding = 0

      return (
        "{{\n"
        "  wd = {0},\n"
        "  mask = {1} {2},\n"
        "  cookie = {3},\n"
        "  name = {4}\n"
        "  len(name) = {5} ({6} padding),\n"
        "}} ({7} bytes)"
      ).format(
        self.wd,
        self.mask,
        Inotify.EventMask(self.mask),
        self.cookie,
        self.name,
        len(self.name),
        padding,
        Inotify.Event.HeaderSize + len(self.name)
      )

    def pack(self):
      return self.wd, self.mask, self.cookie, self.name
