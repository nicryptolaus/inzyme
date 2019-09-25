import logging

class Logger:

  DEFAULT_LOG_FORMAT = (
    "\r%(asctime)s "
    "[%(levelname)s] "
    "[%(name)s:%(process)s]: "
    "%(message)s"
  )

  @staticmethod
  def create(name, level=logging.DEBUG):
    logger = logging.getLogger(name)

    if len(logger.handlers) == 0:
      logger.setLevel(level)
      ch = logging.StreamHandler()
      formatter = logging.Formatter(Logger.DEFAULT_LOG_FORMAT)
      ch.setFormatter(formatter)
      logger.addHandler(ch)

    return logger
