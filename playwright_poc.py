#!/usr/bin/env python3
"""
Playwright Auto Click POC

This script demonstrates multiple ways to automatically click buttons
on a webpage using different locator strategies in Playwright.

The mock website has two buttons:
1. Hamburger Menu (green) - must be clicked first
2. Export Button (blue) - appears after hamburger is clicked (simulates real API)

Configuration:
- Uses user's existing Google Chrome installation
- Opens with user's Default profile
"""

import asyncio
from playwright.async_api import async_playwright
import os


# User's Chrome Configuration
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROME_PROFILE_PATH = "/Users/miit.daga/Library/Application Support/Google/Chrome/Default"

# Time to wait before closing browser (in milliseconds)
WAIT_BEFORE_CLOSE = 5000  # 5 seconds - change this to see browser longer


def get_chrome_context_options():
    """Get Chrome launch options with user profile."""
    return {
        "user_data_dir": CHROME_PROFILE_PATH,
        "headless": False,
        "executable_path": CHROME_PATH,
        "args": [
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
        ],
    }


class AutoClickPOC:
    """Demonstrates various Playwright locator strategies for button clicking."""

    def __init__(self, html_file_path: str):
        """
        Initialize the POC.

        Args:
            html_file_path: Path to the mock HTML file
        """
        self.html_file_path = html_file_path
        self.file_url = f"file://{os.path.abspath(html_file_path)}"

    async def run_with_name_locator(self):
        """
        Method 1: Click buttons using 'name' attribute.
        This is useful when buttons have unique name attributes.
        """
        print("\n" + "=" * 50)
        print("Method 1: Using NAME attribute locators")
        print("=" * 50)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **get_chrome_context_options()
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            print(f"Opened: {self.file_url}")

            # Wait for hamburger button to load
            await page.wait_for_selector('button[name="hamburger"]')

            # Click hamburger menu using name attribute
            print("Clicking hamburger menu using: button[name='hamburger']")
            await page.click('button[name="hamburger"]')

            # Wait for status update
            await page.wait_for_selector('#status:not(:empty)')
            status = await page.text_content('#status')
            print(f"Status: {status}")

            # Wait for export button to appear (simulates real-world dynamic content)
            print("Waiting for export button to appear...")
            await page.wait_for_selector('button[name="export"]', timeout=10000, state="attached")

            # Click export button using name attribute
            print("Clicking export button using: button[name='export']")
            await page.click('button[name="export"]')

            # Wait for final status - increased to let user see the result
            print(f"Waiting {WAIT_BEFORE_CLOSE/1000} seconds before closing...")
            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            print(f"Final Status: {final_status}")

            await context.close()
            print("✓ Method 1 completed successfully!")

    async def run_with_id_locator(self):
        """
        Method 2: Click buttons using 'id' attribute.
        This is the fastest and most reliable method when IDs are unique.
        """
        print("\n" + "=" * 50)
        print("Method 2: Using ID attribute locators")
        print("=" * 50)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **get_chrome_context_options()
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            print(f"Opened: {self.file_url}")

            # Wait for hamburger button
            await page.wait_for_selector('#hamburger-btn')

            # Click using ID selectors
            print("Clicking hamburger menu using: #hamburger-btn")
            await page.click('#hamburger-btn')
            await page.wait_for_selector('#status:not(:empty)')

            # Wait for export button to appear (simulates real-world dynamic content)
            print("Waiting for export button to appear...")
            await page.wait_for_selector('#export-btn', timeout=10000, state="attached")

            print("Clicking export button using: #export-btn")
            await page.click('#export-btn')

            # Wait for final status - increased to let user see the result
            print(f"Waiting {WAIT_BEFORE_CLOSE/1000} seconds before closing...")
            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            print(f"Final Status: {final_status}")

            await context.close()
            print("✓ Method 2 completed successfully!")

    async def run_with_role_locator(self):
        """
        Method 3: Click buttons using 'role' attribute.
        Useful for accessibility-focused automation.
        """
        print("\n" + "=" * 50)
        print("Method 3: Using ROLE attribute locators")
        print("=" * 50)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **get_chrome_context_options()
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            print(f"Opened: {self.file_url}")

            # Wait for hamburger button
            await page.wait_for_selector('button[role="button"][name="hamburger"]')

            # Click hamburger using role + name
            print("Clicking hamburger menu using: button[role='button'][name='hamburger']")
            await page.click('button[role="button"][name="hamburger"]')
            await page.wait_for_selector('#status:not(:empty)')

            # Wait for export button to appear (simulates real-world dynamic content)
            print("Waiting for export button to appear...")
            await page.wait_for_selector('button[role="button"][name="export"]', timeout=10000, state="attached")

            # Click export using role + name
            print("Clicking export button using: button[role='button'][name='export']")
            await page.click('button[role="button"][name="export"]')

            # Wait for final status - increased to let user see the result
            print(f"Waiting {WAIT_BEFORE_CLOSE/1000} seconds before closing...")
            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            print(f"Final Status: {final_status}")

            await context.close()
            print("✓ Method 3 completed successfully!")

    async def run_with_text_locator(self):
        """
        Method 4: Click buttons using text content.
        Useful when you know the button text.
        """
        print("\n" + "=" * 50)
        print("Method 4: Using TEXT content locators")
        print("=" * 50)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **get_chrome_context_options()
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            print(f"Opened: {self.file_url}")

            # Wait for hamburger button
            await page.wait_for_selector('button:has-text("Hamburger Menu")')

            # Click hamburger using text
            print("Clicking button with text: 'Hamburger Menu'")
            await page.click('button:has-text("Hamburger Menu")')
            await page.wait_for_selector('#status:not(:empty)')

            # Wait for export button to appear (simulates real-world dynamic content)
            print("Waiting for export button to appear...")
            await page.wait_for_selector('button:has-text("Export")', timeout=10000, state="attached")

            # Click export using text
            print("Clicking button with text: 'Export'")
            await page.click('button:has-text("Export")')

            # Wait for final status - increased to let user see the result
            print(f"Waiting {WAIT_BEFORE_CLOSE/1000} seconds before closing...")
            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            print(f"Final Status: {final_status}")

            await context.close()
            print("✓ Method 4 completed successfully!")

    async def run_with_data_testid_locator(self):
        """
        Method 5: Click buttons using 'data-testid' attribute.
        Best practice for test automation.
        """
        print("\n" + "=" * 50)
        print("Method 5: Using DATA-TESTID attribute locators")
        print("=" * 50)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **get_chrome_context_options()
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            print(f"Opened: {self.file_url}")

            # Wait for hamburger button
            await page.wait_for_selector('[data-testid="hamburger-menu"]')

            # Click hamburger using data-testid
            print("Clicking hamburger menu using: [data-testid='hamburger-menu']")
            await page.click('[data-testid="hamburger-menu"]')
            await page.wait_for_selector('#status:not(:empty)')

            # Wait for export button to appear (simulates real-world dynamic content)
            print("Waiting for export button to appear...")
            await page.wait_for_selector('[data-testid="export-button"]', timeout=10000, state="attached")

            # Click export using data-testid
            print("Clicking export button using: [data-testid='export-button']")
            await page.click('[data-testid="export-button"]')

            # Wait for final status - increased to let user see the result
            print(f"Waiting {WAIT_BEFORE_CLOSE/1000} seconds before closing...")
            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            print(f"Final Status: {final_status}")

            await context.close()
            print("✓ Method 5 completed successfully!")

    async def run_with_mixed_locators(self):
        """
        Method 6: Use different locators for different buttons.
        Demonstrates flexibility in choosing the best locator for each element.
        """
        print("\n" + "=" * 50)
        print("Method 6: Mixed locator strategies")
        print("=" * 50)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **get_chrome_context_options()
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            print(f"Opened: {self.file_url}")

            # Hamburger: use ID
            print("Hamburger: Clicking using #hamburger-btn")
            await page.click('#hamburger-btn')
            await page.wait_for_selector('#status:not(:empty)')

            # Export: use data-testid
            # Wait for export button to appear (simulates real-world dynamic content)
            print("Waiting for export button to appear...")
            await page.wait_for_selector('[data-testid="export-button"]', timeout=10000, state="attached")

            print("Export: Clicking using [data-testid='export-button']")
            await page.click('[data-testid="export-button"]')

            # Wait for final status - increased to let user see the result
            print(f"Waiting {WAIT_BEFORE_CLOSE/1000} seconds before closing...")
            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            print(f"Final Status: {final_status}")

            await context.close()
            print("✓ Method 6 completed successfully!")

    async def run_all_methods(self):
        """Run all locator methods sequentially."""
        print("\n" + "=" * 60)
        print("Playwright Auto Click POC - All Methods Demonstration")
        print("=" * 60)

        methods = [
            self.run_with_name_locator,
            self.run_with_id_locator,
            self.run_with_role_locator,
            self.run_with_text_locator,
            self.run_with_data_testid_locator,
            self.run_with_mixed_locators,
        ]

        for method in methods:
            try:
                await method()
                print(f"\n✓ {method.__name__} - SUCCESS")
            except Exception as e:
                print(f"\n✗ {method.__name__} - FAILED: {e}")

        print("\n" + "=" * 60)
        print("All methods completed!")
        print("=" * 60)


async def main():
    """Main entry point."""
    # Get the HTML file path
    html_file = os.path.join(os.path.dirname(__file__), 'mock_website.html')

    if not os.path.exists(html_file):
        print(f"Error: HTML file not found at: {html_file}")
        print("Please ensure mock_website.html is in the same directory as this script.")
        return

    # Create and run the POC
    poc = AutoClickPOC(html_file)

    # Run all methods (you can also run individual methods)
    await poc.run_all_methods()

    # Or run just one method:
    # await poc.run_with_name_locator()


if __name__ == "__main__":
    asyncio.run(main())
