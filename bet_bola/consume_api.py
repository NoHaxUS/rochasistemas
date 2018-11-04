import os
import sys
import logging
from daemonize import Daemonize
from updater.up import start_consuming_updates

pid = "test.pid"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
fh = logging.FileHandler("test.log", "w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
keep_fds = [fh.stream.fileno()]


daemon = Daemonize(app="test_app", pid=pid, action=start_consuming_updates, keep_fds=keep_fds)
daemon.start()