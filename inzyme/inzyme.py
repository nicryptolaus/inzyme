import asyncio
import ctypes
import os
import queue
from fcntl import ioctl
from termios import FIONREAD
from inzyme.logger import Logger
from inzyme.inotify_flags import *
from inzyme.inotify import Inotify

class Inzyme(Inotify):
  def __init__(self, *args, **kwargs):
    if "flags" not in kwargs:
        kwargs["flags"] = IN_NONBLOCK
    Inotify.__init__(self, *args, **kwargs)
    self.loop = asyncio.get_running_loop()
    self.logger = Logger.create(self.__class__.__name__)
    self.register(self.event_descriptor, self.process_events)
    self.event_queue = asyncio.Queue()

  def process_events(self, fd, *args):
    bytes_available = ctypes.c_int()
    ioctl(fd, FIONREAD, bytes_available)
    data = os.read(fd, max(bytes_available.value, 1))

    while data is not None and len(data) > 0:
      try:
        event = Inotify.Event.deserialize(data)
        data = data[event.size:]
        self.event_queue.put_nowait(event)
      except Inotify.Error as e:
        self.logger.error("InotifyError: {0}".format(e.message))
        break
      except queue.Full as e:
        self.logger.warning("Queue full")
        break

  def register(self, fd, handler):
    self.loop.add_reader(fd, handler, fd)

  def unregister(self, fd):
    self.loop.remove_reader(fd)
