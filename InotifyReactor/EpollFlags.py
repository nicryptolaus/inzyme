import select

EPOLL_FLAG_NAMES = {
  select.EPOLLIN : 'EPOLLIN',
  select.EPOLLPRI : 'EPOLLPRI',
  select.EPOLLOUT : 'EPOLLOUT',
  select.EPOLLERR : 'EPOLLERR',
  select.EPOLLHUP : 'EPOLLHUP',
}

EPOLL_DEFAULT_EVENTS = (
  select.EPOLLIN  |
  select.EPOLLPRI |
  select.EPOLLOUT
)

EPOLL_ALL_EVENTS = (
  EPOLL_DEFAULT_EVENTS |
  select.EPOLLERR |
  select.EPOLLHUP
)
