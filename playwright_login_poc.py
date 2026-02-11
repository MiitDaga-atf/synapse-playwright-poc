#!/usr/bin/env python3
"""Playwright login automation for mock_login.html."""

import os
from playwright.sync_api import Browser, Page, Playwright, sync_playwright


def login_flow() -> tuple[Playwright, Browser, Page]:
    html_path = os.path.abspath("mock_login.html")
    file_url = f"file:///{html_path.replace('\\', '/')}"
    strix_path = os.path.abspath("strix-mockup-new.html")
    strix_url = f"file:///{strix_path.replace('\\', '/')}"

    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    chrome_exe = next((path for path in chrome_paths if os.path.exists(path)), None)

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
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
    page.goto(strix_url, wait_until="domcontentloaded")
    page.wait_for_url("**/strix-mockup-new.html")

    return playwright, browser, page


def dashboard_export_csv_flow(page: Page) -> None:
    page.locator("#actionsMenuButton").click()
    page.wait_for_selector("#actionsMenuWrap:not([hidden])")
    page.locator("#csvExportMenuItem").click()


if __name__ == "__main__":
    playwright, browser, page = login_flow()
    dashboard_export_csv_flow(page)
    input("Press Enter to close the browser...")
