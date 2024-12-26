from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
import os
import time
from typing import Any

from playwright.sync_api import TimeoutError, sync_playwright

from muteams import WORK_DIR, logger


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

    def _wait_for_selector(self, page, selector):
        try:
            page.wait_for_selector(selector,
                timeout=self.config.TIMEOUT * 1000)
        except TimeoutError:
            logger.debug(f'timed out for {selector}')

    # def _send_message(self, page, message):
    #     selector = 'xpath=//div[@aria-label="Type a message"]'
    #     page.type(selector, message)
    #     page.press(selector, 'Enter')

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

    def run(self):
        state_saved = False
        unread_counts = defaultdict(int)
        with self.playwright_context() as context:
            page = context.new_page()
            page.goto(self.url)
            self._wait_for_selector(page, self.chat_selector)
            while True:
                chat = self._get_unread_chat(page)
                if chat:
                    unread_counts[chat.title] += 1
                    if unread_counts[chat.title] > self.config.RELOAD_MAX_ERRORS:
                        logger.warning('reloading after too many errors')
                        page.reload()
                        continue
                    print(f'marking as read {chat.title}')
                    chat.element.click()
                    time.sleep(1)
                    continue

                unread_counts.clear()
                if not state_saved:
                    context.storage_state(path=self.state_path)
                    state_saved = True
                time.sleep(self.config.LOOP_DELTA)
