# InotifyReactor
Simple monitoring of Linux filesystem events using inotify and epoll in Python 

## Example
```bash
user@host:InotifyReactor$ ./example.py &
[1] 12345
2018-01-08 22:50:16,958 [INFO] [InotifyDaemon:12346]: Starting reactor
2018-01-08 22:50:16,959 [INFO] [InotifyDaemon:12346]: Watching /tmp for events (IN_CLOSE_WRITE)

user@host:InotifyReactor$ touch /tmp/test.txt
2018-01-08 22:50:24,908 [INFO] [InotifyReactor:12346]: process_events(8, (EPOLLIN))
2018-01-08 22:50:24,965 [INFO] [FileProcessor:12345]: Pulled {
  wd = 1,
  mask = 8 (IN_CLOSE_WRITE),
  cookie = 0,
  len = 16,
  name = test.txt
} (32 bytes) from queue

# Send SIGINT
2018-01-08 22:50:41,844 [INFO] [InotifyDaemon:28240]: Shutting down reactor
2018-01-08 22:50:41,986 [INFO] [FileProcessor:28239]: Process Completed
```
