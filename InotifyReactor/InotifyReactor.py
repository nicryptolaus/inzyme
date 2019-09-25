import os
import sys
import ctypes
import errno
import queue
import multiprocessing
from fcntl import ioctl
from termios import FIONREAD
from InotifyReactor.Logger import Logger
from InotifyReactor.EpollReactor import EpollReactor
from InotifyReactor.InotifyFlags import *
from InotifyReactor.Inotify import Inotify

class InotifyReactor(EpollReactor, Inotify):

  def __init__(self, *args, **kwargs):

    EpollReactor.__init__(self, *args, **kwargs)
    Inotify.__init__(self, *args, **kwargs)

    self.qsize = 4 if "qsize" not in kwargs else kwargs["qsize"]
    self.event_queue = multiprocessing.Queue(self.qsize) if "queue" not in \
      kwargs else kwargs["queue"]
    self.logger = Logger.create(self.__class__.__name__)

    self.register(self.event_descriptor, self.process_events)

  def process_events(self, fd, flags):
    bytes_available = ctypes.c_int()
    ioctl(fd, FIONREAD, bytes_available)
    data = os.read(fd, max(bytes_available.value, 1))

    maskStr = EpollReactor.EventMask(flags)
    self.logger.info("process_events({0}, {1})".format(fd, maskStr))

    while data is not None and len(data) > 0:
      try:
        event = Inotify.Event.deserialize(data)
        data = data[event.size:]
        self.event_queue.put_nowait((event.pack(),))
      except Inotify.Error as e:
        self.logger.error("InotifyError: {0}".format(e.message))
        break
      except queue.Full as e:
        self.logger.warning("Queue full")
        break

  def getEventQueue(self):
    return self.event_queue
