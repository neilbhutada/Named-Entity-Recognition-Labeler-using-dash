import multiprocessing
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import time
from urllib.request import urlopen, URLError

import pytest
from playwright.sync_api import sync_playwright, Error
import working_demo


@pytest.fixture(scope="module")
def server():
    process = multiprocessing.Process(target=working_demo.app.run, kwargs={"port": 8051, "debug": False})
    process.start()
    for _ in range(10):
        try:
            urlopen("http://127.0.0.1:8051")
            break
        except URLError:
            time.sleep(1)
    yield
    process.terminate()
    process.join()


def test_labeling_flow(server):
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Error:
            pytest.skip("Chromium browser not installed")
        page = browser.new_page()
        page.goto("http://127.0.0.1:8051")

        assert "No entities labeled yet." in page.locator("#entities-display").inner_text()

        page.evaluate("""
            const el = document.getElementById('text-display');
            const selection = window.getSelection();
            selection.removeAllRanges();
            const range = document.createRange();
            range.selectNodeContents(el);
            selection.addRange(range);
        """)

        page.click("#btn-person")
        page.wait_for_selector("#entities-display div")
        assert "PERSON" in page.locator("#entities-display").inner_text()

        browser.close()
