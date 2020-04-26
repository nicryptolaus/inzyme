#!/usr/bin/env python

from optparse import OptionParser
from inzyme.inotify import *
from inzyme.inzyme import *

class FileProcessor():
  """ Example class making use of Inzyme """

  def __init__(self, *args, **kwargs):
    if 'options' not in kwargs:
      raise ValueError("No options specified")

    self.logger = Logger.create(self.__class__.__name__)
    self.directory = kwargs['options'].directory
    self.watcher = Inzyme()
    self.eventMask = IN_ALL_EVENTS
    self.watcher.add_watch(self.directory, self.eventMask)

  async def get_event(self):
    return await self.watcher.event_queue.get()

  def run_worker(self, event):
    self.logger.info(event)

def parse_cmdline():
  parser = OptionParser()
  parser.add_option("-d", "--dir", dest="directory", default='/tmp',
            help="directory to monitor")
  return parser.parse_args()

async def main():
  (options, args) = parse_cmdline()
  processor = FileProcessor(options=options)

  while asyncio.get_running_loop().is_running():
    event = await processor.get_event()
    processor.run_worker(event)

if __name__ == '__main__':
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    pass
