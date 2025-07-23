import logging
import os

WORK_DIR = os.path.expanduser('~/tmp/tests/muteams')
os.makedirs(WORK_DIR, exist_ok=True)
import muteams as module
module.WORK_DIR = WORK_DIR
logging.getLogger('').handlers.clear()
