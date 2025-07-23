import os
import shutil
import unittest

from tests import WORK_DIR
from muteams import teams as module
from svcutils.service import Config


def remove_path(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


class TestTestCase(unittest.TestCase):
    def setUp(self):
        # remove_path(WORK_DIR)
        os.makedirs(WORK_DIR, exist_ok=True)
        self.config = Config(
            __file__,
            MARK_AS_READ_CHATS=['Constance', 'Clémence'],
            HEADLESS=False,
            TIMEOUT=60,
            LOOP_DELTA=10,
            RELOAD_MAX_ATTEMPTS=10,
        )

    def test_1(self):
        module.Muteams(self.config).run()
