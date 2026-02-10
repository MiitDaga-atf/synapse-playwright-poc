#!/usr/bin/env python3
"""Playwright login automation for mock_login.html."""

import os
from playwright.sync_api import sync_playwright


def main() -> None:
    html_path = os.path.abspath("mock_login.html")
    file_url = f"file:///{html_path.replace('\\', '/')}"

    with sync_playwright() as p:
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        chrome_exe = next((path for path in chrome_paths if os.path.exists(path)), None)

        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            executable_path=chrome_exe,
        )
        page = browser.new_page()

        page.goto(file_url, wait_until="domcontentloaded")

        page.locator('input[name="email"]').fill("abcd")
        page.locator('input[name="password"]').fill("abcd")
        page.locator('[data-testid="login-button"]').click()

        page.wait_for_url("**/login_success.html")
        page.wait_for_timeout(2000)

        browser.close()


if __name__ == "__main__":
    main()
