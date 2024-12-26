from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
import os
import time
from typing import Any

from playwright.sync_api import sync_playwright

from muteams import WORK_DIR, logger


MAX_ATTEMPTS = 10


@dataclass
class UnreadChat:
    title: str
    element: Any


class Muteams:
    url = 'https://teams.microsoft.com/v2/'
    chat_selector = 'xpath=//span[@data-tid="chat-list-item-title"]'
    unread_selector = 'xpath=//div[contains(@class, "chatListItem_unreadIndicator")]/..'
    title_selector = 'xpath=.//div[3]/div/span'

    def __init__(self, config):
        self.config = config
        self.work_dir = WORK_DIR
        self.state_path = os.path.join(self.work_dir, 'state.json')
        if not self.config.MARK_AS_READ_CHATS:
            raise Exception('missing MARK_AS_READ_CHATS')

    @contextmanager
    def playwright_context(self):
        with sync_playwright() as p:
            context = None
            try:
                browser = p.chromium.launch(
                    headless=self.config.HEADLESS,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                    ],
                )
                context = browser.new_context(storage_state=self.state_path
                    if os.path.exists(self.state_path) else None)
                yield context
            finally:
                if context:
                    context.close()

    def _must_mark_as_read(self, title):
        for mark_as_read_chat in self.config.MARK_AS_READ_CHATS:
            if mark_as_read_chat in title:
                return True
        return False

    def _get_unread_chat(self, page):
        for unread_element in page.locator(self.unread_selector).all():
            elements = unread_element.locator(self.title_selector).all()
            if not elements:
                continue
            title = elements[0].text_content().strip()
            if self._must_mark_as_read(title):
                return UnreadChat(title=title, element=elements[0])

    def _select_oldest_chat(self, page):
        chats = page.locator(self.chat_selector).all()
        if chats:
            chats[-1].click()

    def run(self):
        state_saved = False
        attempts = defaultdict(int)
        with self.playwright_context() as context:
            page = context.new_page()
            page.goto(self.url)
            page.wait_for_selector(self.chat_selector,
                timeout=self.config.TIMEOUT * 1000)
            while True:
                try:
                    chat = self._get_unread_chat(page)
                    if chat:
                        attempts[chat.title] += 1
                        if attempts[chat.title] > MAX_ATTEMPTS:
                            logger.error('reloading after too many attempts')
                            page.reload()
                            attempts.clear()
                            continue
                        logger.info(f'marking as read {chat.title}')
                        chat.element.click()
                        time.sleep(1)
                        self._select_oldest_chat(page)
                        continue

                    self._select_oldest_chat(page)
                    attempts.clear()
                    if not state_saved:
                        context.storage_state(path=self.state_path)
                        state_saved = True
                except Exception:
                    logger.exception('wtf')
                time.sleep(self.config.LOOP_DELTA)
