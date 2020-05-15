# inzyme
Simple monitoring of Linux filesystem events using inotify in Python 

## Example
```bash
user@host:inzyme$ python3.7 example.py -d . &
[1] 12345

user@host:inzyme$ touch test.txt
2020-05-14 22:15:41,109 [INFO] [FileProcessor]: {
  wd = 1,
  mask = (IN_OPEN),
  cookie = 0,
  name = test.txt
}
2020-05-14 22:15:41,110 [INFO] [FileProcessor]: {
  wd = 1,
  mask = (IN_ATTRIB),
  cookie = 0,
  name = test.txt
}
2020-05-14 22:15:41,110 [INFO] [FileProcessor]: {
  wd = 1,
  mask = (IN_CLOSE_WRITE),
  cookie = 0,
  name = test.txt
}
```
