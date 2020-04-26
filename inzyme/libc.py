import ctypes

class libc:
  """ ctypes wrapper for system-calls """
  lib = ctypes.cdll.LoadLibrary("libc.so.6")

  @classmethod
  def inotify_init1(cls, flags):
    return libc.lib.inotify_init1(flags)

  @classmethod
  def inotify_add_watch(cls, fd, pathname, mask):
    return libc.lib.inotify_add_watch(fd, pathname, mask)

  @classmethod
  def inotify_rm_watch(cls, fd, wd):
    return libc.lib.inotify_rm_watch(fd, wd)
