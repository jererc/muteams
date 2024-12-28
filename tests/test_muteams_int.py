import logging
import os
import shutil
import unittest
from unittest.mock import patch

from svcutils.service import Config

import muteams as module
WORK_DIR = os.path.join(os.path.expanduser('~'), '_tests', 'muteams')
module.WORK_DIR = WORK_DIR
module.logger.setLevel(logging.DEBUG)
module.logger.handlers.clear()
from muteams import teams as module


module.logger.setLevel(logging.DEBUG)


def remove_path(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


class TestTestCase(unittest.TestCase):
    def setUp(self):
        # remove_path(WORK_DIR)
        makedirs(WORK_DIR)
        self.config = Config(__file__,
            MARK_AS_READ_CHATS=['Constance', 'Clémence'],
            HEADLESS=False,
            TIMEOUT=60,
            LOOP_DELTA=10,
            RELOAD_MAX_ATTEMPTS=10,
        )

    def test_1(self):
        module.Muteams(self.config).run()
