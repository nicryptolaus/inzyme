#!/usr/bin/env python

import time
import socket
import Queue
from optparse import OptionParser
from InotifyReactor.InotifyDaemon import *

class FileProcessor(object):
  """ Example class making use of InotifyReactor within a child process """

  def __init__(self, *args, **kwargs):

    if 'options' not in kwargs:
      raise ValueError("No options specified")

    self.logger = Logger.create(self.__class__.__name__)
    self.fileMonitor = InotifyDaemon(kwargs['options'].directory)

def parse_cmdline():
  parser = OptionParser()
  parser.add_option("-d", "--dir", dest="directory", default='/tmp',
            help="directory to monitor")

  (options, args) = parser.parse_args()

  return (options, args)

def get_lock(process_name):
  get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

  try:
    get_lock._lock_socket.bind('\0' + process_name)
  except socket.error:
    print 'FileProcessor is already running'
    sys.exit()

def main():
  # Ignore SIGINT
  signal.signal(signal.SIGINT, signal.SIG_IGN)

  # Only run one instance
  get_lock('FileProcessor')

  (options, args) = parse_cmdline()
  processor = FileProcessor(options=options)

  # Start reactor in separate process
  processor.fileMonitor.start()

  while processor.fileMonitor.is_alive():
    try:
      for event in processor.fileMonitor.eventQueue.get_nowait():
        e = Inotify.Event(*event)
        processor.logger.info("Pulled {0} from queue".format(e))
    except Queue.Empty as e:
      # Queue is empty, do something else for a while
      time.sleep(.1)
      pass
    except Exception as e:
      processor.logger.info("Encountered an exception: {0}".format(e))
      pass

  processor.fileMonitor.join()
  processor.logger.info("Process Completed")

if __name__ == '__main__':
  main()
