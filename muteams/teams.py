from contextlib import contextmanager
import os
import time

from playwright.sync_api import TimeoutError, sync_playwright

from muteams import WORK_DIR, logger


class Muteams:
    url = 'https://teams.microsoft.com/v2/'

    def __init__(self, config):
        self.config = config
        self.work_dir = WORK_DIR
        self.state_path = os.path.join(self.work_dir, 'state.json')

    @contextmanager
    def playwright_context(self):
        with sync_playwright() as p:
            context = None
            try:
                browser = p.chromium.launch(
                    headless=True,
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

    def _mark_as_read_if_required(self, page, unread_element, timeout=5):
        if not self.config.MARK_AS_READ_CHATS:
            return
        title_selector = 'xpath=.//div[3]/div/span'
        elements = unread_element.locator(title_selector).all()
        if not elements:
            logger.warning(f'failed to find {title_selector}')
            return
        title = elements[0].text_content().strip()
        if not self._must_mark_as_read(title):
            return
        print(f'marking as read {title}')
        unread_element.click()
        end_ts = time.time() + timeout
        while time.time() < end_ts:
            if not unread_element.locator('xpath=.//div').all():
                return
            time.sleep(.2)

    def run(self):
        state_saved = False
        with self.playwright_context() as context:
            page = context.new_page()
            page.goto(self.url)
            # menu_selector = 'xpath=//div[@aria-label="Chat"]'
            chat_selector = 'xpath=//span[@data-tid="chat-list-item-title"]'
            unread_selector = 'xpath=//div[contains(@class, "chatListItem_unreadIndicator")]/..'
            while True:
                self._wait_for_selector(page, chat_selector)
                for unread_element in page.locator(unread_selector).all():
                    self._mark_as_read_if_required(page, unread_element)
                if not state_saved:
                    context.storage_state(path=self.state_path)
                    state_saved = True
                time.sleep(self.config.LOOP_DELTA)
