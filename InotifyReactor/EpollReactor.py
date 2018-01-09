import os
import sys
import signal
import select
import ctypes
import errno
import multiprocessing
from fcntl import ioctl
from EpollFlags import *
from Utils import splitMask
from termios import FIONREAD

class EpollReactor(object):
  """ Manages file descriptors registered with epoll instance and their
      callbacks """

  def __init__(self, *args, **kwargs):
    super(EpollReactor, self).__init__(*args, **kwargs)
    self.reactor = select.epoll()
    self.state = EpollReactor.State.Stopped
    self.descriptors = {}

  def register(self, fd, callback, eventmask = EPOLL_DEFAULT_EVENTS):
    """ Register a file descriptor/eventmask with epoll instance. The supplied
        callback will be called for each event with
        (fd, event flags, raw bytes) as arguments """
    if fd not in self.descriptors:
      self.reactor.register(fd, eventmask)
      self.descriptors[fd] = { 'callback': callback }

  def unregister(self, fd):
    """ Remove descriptor """
    if fd in self.descriptors:
      self.reactor.unregister(fd)

  def run(self):
    self.register_signal_handlers()
    self.state = EpollReactor.State.Running

    try:
      while(EpollReactor.State.Running == self.state):
        for fd, mask in self.reactor.poll():
          bytes_available = ctypes.c_int()
          ioctl(fd, FIONREAD, bytes_available)
          data = os.read(fd, max(bytes_available.value, 1))
          self.descriptors[fd]['callback'](fd, mask, data)
    except IOError, e:
      if e.errno != errno.EINTR:
        raise EpollReactor.Error(e)

  def shutdown(self):
    """ Unregister all descriptors and stop epoll instance """
    for fd in self.descriptors:
      self.reactor.unregister(fd)
    self.reactor.close()

  def sigint_handler(self, signum, frame):
    """ Shutdown event loop """
    self.state = EpollReactor.State.Stopped

  def register_signal_handlers(self):
    """ Register signal handler for shutdown on SIGINT """
    signal.signal(signal.SIGINT, self.sigint_handler)

  class Error(Exception):
    """ EpollReactor exceptions """
    def __init__(self, message, errors = None):
      super(EpollReactor.Error, self).__init__(message)
      self.errors = errors

  class State(object):
    """ Possible run-states for reactor """
    Stopped, Running = range(2)

  class EventMask(object):
    """ Utility for printing mask as a pipe-delimited string """
    def __init__(self, mask):
      self.mask = mask

    def __str__(self):
      return '(' + ' | '.join(splitMask(self.mask, EPOLL_FLAG_NAMES)) + ')'
