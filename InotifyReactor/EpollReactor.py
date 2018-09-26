import os
import sys
import signal
import select
import errno
import multiprocessing
from EpollFlags import *
from Utils import splitMask

class EpollReactor(object):
  """ Manages file descriptors registered with epoll instance and their
      callbacks """

  def __init__(self, *args, **kwargs):
    super(EpollReactor, self).__init__(*args, **kwargs)
    self.reactor = select.epoll()
    self.state = EpollReactor.State.Stopped
    self.handlers = {}

  def register(self, fd, handler, eventmask = EPOLL_DEFAULT_EVENTS):
    """ Register a file descriptor/eventmask with epoll instance. The supplied
        handler will be called for each event with
        (fd, eventmask) as arguments """
    if fd not in self.handlers:
      self.reactor.register(fd, eventmask)
      self.handlers[fd] = handler
    else:
      raise EpollReactor.Error("Descriptor already registered")

  def unregister(self, fd):
    """ Remove descriptor """
    if fd in self.handlers:
      self.reactor.unregister(fd)
      del self.handlers[fd]
    else:
      raise EpollReactor.Error("Descriptor not found")

  def run(self):
    self.register_signal_handlers()
    self.state = EpollReactor.State.Running

    try:
      while(EpollReactor.State.Running == self.state):
        for fd, mask in self.reactor.poll():
          self.handlers[fd](fd, mask)
    except IOError, e:
      if e.errno != errno.EINTR:
        raise EpollReactor.Error(e.message)

  def shutdown(self):
    """ Unregister all handlers and stop epoll instance """
    for fd in self.handlers:
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
