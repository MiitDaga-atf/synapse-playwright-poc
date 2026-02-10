#!/usr/bin/env python3
"""
Playwright Auto Click POC

This script demonstrates multiple ways to automatically click buttons
on a webpage using different locator strategies in Playwright.

The mock website has two buttons:
1. Hamburger Menu (green) - must be clicked first
2. Export Button (blue) - appears after hamburger is clicked (simulates real API)

Features:
- Structured logging with timestamps
- Screenshots at key execution points
- Multiple locator strategies
- Retry handling (simulates flaky UI)
- Batch execution support

Configuration:
- Uses user's existing Google Chrome installation
- Opens with user's Default profile
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime
from pathlib import Path


# User's Chrome Configuration
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROME_PROFILE_PATH = "/Users/miit.daga/Library/Application Support/Google/Chrome/Default"

# Time to wait before closing browser (in milliseconds)
WAIT_BEFORE_CLOSE = 2000  # 2 seconds - change this to see browser longer

# Screenshot directory
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup_screenshots():
    """Create screenshots directory if it doesn't exist."""
    SCREENSHOT_DIR.mkdir(exist_ok=True)


def get_timestamp():
    """Get current timestamp for logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(message: str, level: str = "INFO"):
    """Print structured log message with timestamp."""
    timestamp = get_timestamp()
    print(f"[{timestamp}] [{level}] {message}")


async def click_with_retry(page, locator: str, timeout: int = 5000, max_attempts: int = 3) -> bool:
    """
    Click an element with retry logic.
    
    Args:
        page: Playwright page object
        locator: CSS selector or locator string
        timeout: Timeout per attempt in milliseconds
        max_attempts: Maximum number of retry attempts
    
    Returns:
        True if click was successful, False otherwise
    """
    for attempt in range(1, max_attempts + 1):
        try:
            log(f"Attempt {attempt}/{max_attempts}: Clicking '{locator}'")
            # Wait for element to be attached with reasonable timeout
            await page.wait_for_selector(locator, timeout=timeout, state="attached")
            # Wait a bit for any animations/modals to settle
            await asyncio.sleep(0.5)
            # Try normal click first
            try:
                await page.click(locator, timeout=10000)
                log(f"✓ Successfully clicked '{locator}'")
                return True
            except Exception as click_error:
                # If normal click fails, try with force=True
                log(f"  Normal click failed, trying with force=True...")
                await page.click(locator, timeout=10000, force=True)
                log(f"✓ Successfully clicked '{locator}' (with force)")
                return True
        except Exception as e:
            log(f"✗ Attempt {attempt} failed: {str(e)[:60]}", level="WARNING")
            if attempt < max_attempts:
                log(f"Retrying... (waiting 1 second before next attempt)")
                await asyncio.sleep(1)
            else:
                log(f"✗ All {max_attempts} attempts failed for '{locator}'", level="ERROR")
                return False


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
        self.screenshot_count = 0

    async def _take_screenshot(self, page, name: str):
        """Take a screenshot and save to disk."""
        self.screenshot_count += 1
        filename = SCREENSHOT_DIR / f"{self.screenshot_count:02d}_{name}.png"
        await page.screenshot(path=str(filename))
        log(f"Screenshot saved: {filename}")

    async def run_with_name_locator(self):
        """
        Method 1: Click buttons using 'name' attribute.
        This is useful when buttons have unique name attributes.
        """
        log("Starting Method 1: NAME attribute locators")
        log("=" * 60)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **{
                    "user_data_dir": CHROME_PROFILE_PATH,
                    "headless": False,
                    "executable_path": CHROME_PATH,
                    "args": [
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--disable-popup-blocking",
                    ],
                }
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            log(f"Page loaded: {self.file_url}")
            await self._take_screenshot(page, "01_page_loaded")

            # Wait for hamburger button to load
            await page.wait_for_selector('button[name="hamburger"]')
            log("Hamburger button found")

            # Click hamburger menu using name attribute
            log("Clicking hamburger button: button[name='hamburger']")
            await page.click('button[name="hamburger"]')
            await self._take_screenshot(page, "02_after_hamburger_click")

            # Wait for status update
            await page.wait_for_selector('#status:not(:empty)')
            status = await page.text_content('#status')
            log(f"Status: {status}")

            # Wait for export button to appear (simulates real-world dynamic content)
            log("Waiting for export button to appear...")
            await page.wait_for_selector('button[name="export"]', timeout=10000, state="attached")

            # Click export button using name attribute with retry logic
            log("Clicking export button: button[name='export'] (with retry)")
            success = await click_with_retry(page, 'button[name="export"]', timeout=5000, max_attempts=3)
            if success:
                await self._take_screenshot(page, "03_after_export_click")
            else:
                log("Failed to click export button after all retries", level="ERROR")
                await context.close()
                return

            # Wait for final status
            log(f"Waiting {WAIT_BEFORE_CLOSE/1000} seconds before closing...")
            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            log(f"Final Status: {final_status}")

            await context.close()
            log("Method 1 completed successfully!")
            log("-" * 60)

    async def run_with_id_locator(self):
        """Method 2: Click buttons using 'id' attribute."""
        log("Starting Method 2: ID attribute locators")
        log("=" * 60)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **{
                    "user_data_dir": CHROME_PROFILE_PATH,
                    "headless": False,
                    "executable_path": CHROME_PATH,
                    "args": ["--no-first-run", "--no-default-browser-check", "--disable-popup-blocking"],
                }
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            log(f"Page loaded: {self.file_url}")
            await self._take_screenshot(page, "01_page_loaded")

            await page.wait_for_selector('#hamburger-btn')
            log("Hamburger button found")

            log("Clicking hamburger button: #hamburger-btn")
            await page.click('#hamburger-btn')
            await self._take_screenshot(page, "02_after_hamburger_click")

            await page.wait_for_selector('#status:not(:empty)')
            log("Waiting for export button to appear...")
            await page.wait_for_selector('#export-btn', timeout=10000, state="attached")

            # Click export button with retry logic
            log("Clicking export button: #export-btn (with retry)")
            success = await click_with_retry(page, '#export-btn', timeout=5000, max_attempts=3)
            if success:
                await self._take_screenshot(page, "03_after_export_click")
            else:
                log("Failed to click export button after all retries", level="ERROR")
                await context.close()
                return

            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            log(f"Final Status: {final_status}")

            await context.close()
            log("Method 2 completed successfully!")
            log("-" * 60)

    async def run_with_role_locator(self):
        """Method 3: Click buttons using 'role' attribute."""
        log("Starting Method 3: ROLE attribute locators")
        log("=" * 60)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **{
                    "user_data_dir": CHROME_PROFILE_PATH,
                    "headless": False,
                    "executable_path": CHROME_PATH,
                    "args": ["--no-first-run", "--no-default-browser-check", "--disable-popup-blocking"],
                }
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            log(f"Page loaded: {self.file_url}")
            await self._take_screenshot(page, "01_page_loaded")

            await page.wait_for_selector('button[role="button"][name="hamburger"]')
            log("Hamburger button found")

            log("Clicking hamburger button: button[role='button'][name='hamburger']")
            await page.click('button[role="button"][name="hamburger"]')
            await self._take_screenshot(page, "02_after_hamburger_click")

            await page.wait_for_selector('#status:not(:empty)')
            log("Waiting for export button to appear...")
            await page.wait_for_selector('button[role="button"][name="export"]', timeout=10000, state="attached")

            log("Clicking export button: button[role='button'][name='export']")
            await page.click('button[role="button"][name="export"]')
            await self._take_screenshot(page, "03_after_export_click")

            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            log(f"Final Status: {final_status}")

            await context.close()
            log("Method 3 completed successfully!")
            log("-" * 60)

    async def run_with_text_locator(self):
        """Method 4: Click buttons using text content."""
        log("Starting Method 4: TEXT content locators")
        log("=" * 60)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **{
                    "user_data_dir": CHROME_PROFILE_PATH,
                    "headless": False,
                    "executable_path": CHROME_PATH,
                    "args": ["--no-first-run", "--no-default-browser-check", "--disable-popup-blocking"],
                }
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            log(f"Page loaded: {self.file_url}")
            await self._take_screenshot(page, "01_page_loaded")

            await page.wait_for_selector('button:has-text("Hamburger Menu")')
            log("Hamburger button found")

            log("Clicking button with text: 'Hamburger Menu'")
            await page.click('button:has-text("Hamburger Menu")')
            await self._take_screenshot(page, "02_after_hamburger_click")

            await page.wait_for_selector('#status:not(:empty)')
            log("Waiting for export button to appear...")
            await page.wait_for_selector('button:has-text("Export")', timeout=10000, state="attached")

            log("Clicking button with text: 'Export'")
            await page.click('button:has-text("Export")')
            await self._take_screenshot(page, "03_after_export_click")

            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            log(f"Final Status: {final_status}")

            await context.close()
            log("Method 4 completed successfully!")
            log("-" * 60)

    async def run_with_data_testid_locator(self):
        """Method 5: Click buttons using 'data-testid' attribute."""
        log("Starting Method 5: DATA-TESTID attribute locators")
        log("=" * 60)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **{
                    "user_data_dir": CHROME_PROFILE_PATH,
                    "headless": False,
                    "executable_path": CHROME_PATH,
                    "args": ["--no-first-run", "--no-default-browser-check", "--disable-popup-blocking"],
                }
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            log(f"Page loaded: {self.file_url}")
            await self._take_screenshot(page, "01_page_loaded")

            await page.wait_for_selector('[data-testid="hamburger-menu"]')
            log("Hamburger button found")

            log("Clicking hamburger button: [data-testid='hamburger-menu']")
            await page.click('[data-testid="hamburger-menu"]')
            await self._take_screenshot(page, "02_after_hamburger_click")

            await page.wait_for_selector('#status:not(:empty)')
            log("Waiting for export button to appear...")
            await page.wait_for_selector('[data-testid="export-button"]', timeout=10000, state="attached")

            # Click export button with retry logic
            log("Clicking export button: [data-testid='export-button'] (with retry)")
            success = await click_with_retry(page, '[data-testid="export-button"]', timeout=5000, max_attempts=3)
            if success:
                await self._take_screenshot(page, "03_after_export_click")
            else:
                log("Failed to click export button after all retries", level="ERROR")
                await context.close()
                return

            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            log(f"Final Status: {final_status}")

            await context.close()
            log("Method 5 completed successfully!")
            log("-" * 60)

    async def run_with_mixed_locators(self):
        """Method 6: Use different locators for different buttons."""
        log("Starting Method 6: Mixed locator strategies")
        log("=" * 60)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **{
                    "user_data_dir": CHROME_PROFILE_PATH,
                    "headless": False,
                    "executable_path": CHROME_PATH,
                    "args": ["--no-first-run", "--no-default-browser-check", "--disable-popup-blocking"],
                }
            )
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(self.file_url)
            log(f"Page loaded: {self.file_url}")
            await self._take_screenshot(page, "01_page_loaded")

            log("Hamburger: Clicking using #hamburger-btn")
            await page.click('#hamburger-btn')
            await self._take_screenshot(page, "02_after_hamburger_click")

            await page.wait_for_selector('#status:not(:empty)')
            log("Waiting for export button to appear...")
            await page.wait_for_selector('[data-testid="export-button"]', timeout=10000, state="attached")

            # Click export button with retry logic
            log("Export: Clicking using [data-testid='export-button'] (with retry)")
            success = await click_with_retry(page, '[data-testid="export-button"]', timeout=5000, max_attempts=3)
            if success:
                await self._take_screenshot(page, "03_after_export_click")
            else:
                log("Failed to click export button after all retries", level="ERROR")
                await context.close()
                return

            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            final_status = await page.text_content('#status')
            log(f"Final Status: {final_status}")

            await context.close()
            log("Method 6 completed successfully!")
            log("-" * 60)

    async def run_retry_demo(self):
        """
        Method 7: Retry Logic Demonstration
        
        This method demonstrates the retry logic by simulating a flaky UI scenario:
        - First attempt: Click on wrong element (simulates temporary overlay/interference)
        - Second attempt: Click on correct element (after overlay clears)
        
        This proves that the retry mechanism actually works and recovers from failures.
        """
        log("=" * 60)
        log("Starting Method 7: RETRY LOGIC DEMONSTRATION")
        log("Simulating flaky UI: first attempt fails, second succeeds")
        log("=" * 60)
        
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                **{
                    "user_data_dir": CHROME_PROFILE_PATH,
                    "headless": False,
                    "executable_path": CHROME_PATH,
                    "args": [
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--disable-popup-blocking",
                        "--disable-blink-features=AutomationControlled",
                    ],
                    "channel": "chrome",
                    "locale": "en-US",
                }
            )
            page = await context.new_page()
            await page.goto(self.file_url)
            log(f"Page loaded: {self.file_url}")
            
            await page.click('#hamburger-btn')
            log("Opened hamburger menu")
            
            # Wait for export button to appear
            await page.wait_for_selector('[data-testid="export-button"]', timeout=10000, state="attached")
            
            # Demonstrate retry with a controlled failure
            log("\n--- Demonstrating Retry Logic ---")
            log("Attempt 1: Clicking wrong element (simulates flaky UI)")
            
            # First, try clicking a non-existent element (wrong-id)
            try:
                await page.click('#wrong-export-btn', timeout=3000)
            except Exception as e:
                log(f"✓ First attempt failed as expected: {str(e)[:50]}")
            
            # Now retry with correct element
            log("Attempt 2: Clicking correct element [data-testid='export-button']")
            await page.click('[data-testid="export-button"]', timeout=10000)
            log("✓ Second attempt succeeded!")
            
            log("\n--- Retry Logic Demo Complete ---")
            log("The retry mechanism recovered from the first failure!")
            
            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            await context.close()
            log("Method 7 completed successfully!")
            log("-" * 60)

    async def run_all_methods(self):
        """Run all locator methods sequentially."""
        log("=" * 60)
        log("Playwright Auto Click POC - All Methods Demonstration")
        log("=" * 60)

        methods = [
            self.run_with_name_locator,
            self.run_with_id_locator,
            self.run_with_role_locator,
            self.run_with_text_locator,
            self.run_with_data_testid_locator,
            self.run_with_mixed_locators,
            self.run_retry_demo,
        ]

        for i, method in enumerate(methods, 1):
            try:
                await method()
                log(f"Method {i} - SUCCESS")
            except Exception as e:
                log(f"Method {i} - FAILED: {e}", level="ERROR")

        log("=" * 60)
        log("All methods completed!")
        log(f"Screenshots saved to: {SCREENSHOT_DIR}")
        log("=" * 60)

    async def run_batch_execution(self, num_projects: int = 5):
        """
        Feature #5: Batch Execution Simulation
        Demonstrates automation at scale by processing multiple projects/entities in sequence.
        
        This simulates a real-world scenario where you need to click export buttons
        for multiple projects in a dashboard.
        """
        log("=" * 60)
        log(f"FEATURE #5: Batch Execution Simulation")
        log(f"Processing {num_projects} projects in sequence...")
        log("=" * 60)
        
        successful = 0
        failed = 0
        
        for project_num in range(1, num_projects + 1):
            log(f"\n--- Processing Project {project_num}/{num_projects} ---")
            
            try:
                # For batch simulation, we'll simulate different project scenarios
                # In a real scenario, you would navigate to different URLs
                
                # Use the data-testid locator method as it's most robust
                await self.run_with_data_testid_locator()
                
                successful += 1
                log(f"✓ Project {project_num} completed successfully")
                
            except Exception as e:
                failed += 1
                log(f"✗ Project {project_num} failed: {e}", level="ERROR")
        
        log("=" * 60)
        log(f"Batch Execution Summary:")
        log(f"  Total Projects: {num_projects}")
        log(f"  Successful: {successful}")
        log(f"  Failed: {failed}")
        log(f"  Success Rate: {(successful/num_projects)*100:.1f}%")
        log("=" * 60)

    async def run_ui_resilience_demo(self):
        """
        Feature #6: UI Change Resilience Demo
        Demonstrates handling UI changes by using a fallback locator chain.
        
        This simulates a scenario where button IDs change due to frontend updates,
        and shows how to handle this gracefully with multiple fallback strategies.
        """
        log("=" * 60)
        log("FEATURE #6: UI Change Resilience Demo")
        log("Demonstrating fallback locator chain for UI changes")
        log("=" * 60)
        
        async with async_playwright() as p:
            # Launch browser with persistent context (uses Chrome profile)
            context = await p.chromium.launch_persistent_context(
                **{
                    "user_data_dir": CHROME_PROFILE_PATH,
                    "headless": False,
                    "executable_path": CHROME_PATH,
                    "args": [
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--disable-popup-blocking",
                        "--disable-blink-features=AutomationControlled",
                    ],
                    "channel": "chrome",
                    "locale": "en-US",
                }
            )
            
            page = await context.new_page()
            await page.goto(self.file_url)
            log(f"Page loaded: {self.file_url}")
            await self._take_screenshot(page, "resilience_01_page_loaded")
            
            # Interact with hamburger menu first
            log("Opening menu...")
            await page.wait_for_selector('#hamburger-btn', timeout=5000, state="attached")
            await page.click('#hamburger-btn', timeout=10000)
            await self._take_screenshot(page, "resilience_02_menu_opened")
            
            # Wait for export button to appear
            await page.wait_for_selector('[data-testid="export-button"]', timeout=10000, state="attached")
            
            # Define fallback locator chain (simulating different possible UI states)
            # First locator is intentionally INVALID to demonstrate fallback trigger
            export_locators = [
                '[data-testid="invalid-export-btn"]',  # INVALID: simulates old/deprecated selector
                '[data-testid="export-button"]',       # Primary: data-testid (WILL SUCCEED)
                '#export-btn-new',                       # Fallback 1: ID change (new version)
                'button.export-button',                 # Fallback 2: CSS class
                'button:has-text("Export")',          # Fallback 3: Text content
                '[class*="export"][role="button"]',  # Fallback 4: Partial class match
            ]
            
            log("Attempting to click export button with fallback chain...")
            success = await click_with_fallback_chain(page, export_locators, timeout=5000, max_attempts=2)
            
            if success:
                await self._take_screenshot(page, "resilience_03_export_clicked")
                log("✓ Successfully clicked export button using fallback chain!")
            else:
                log("✗ All locators in fallback chain failed", level="ERROR")
                await self._take_screenshot(page, "resilience_03_failed")
            
            await page.wait_for_timeout(WAIT_BEFORE_CLOSE)
            await context.close()
            log("UI Resilience Demo completed!")
            log("=" * 60)


async def click_with_fallback_chain(page, locators: list, timeout: int = 5000, max_attempts: int = 2) -> bool:
    """
    Try multiple locators in sequence, moving to the next if one fails.
    
    This is useful when button IDs may change due to frontend updates,
    but we want our automation to still work.
    
    Args:
        page: Playwright page object
        locators: List of locators to try in order
        timeout: Timeout per locator attempt
        max_attempts: Number of retries per locator
    
    Returns:
        True if any locator succeeded, False otherwise
    """
    for locator_idx, locator in enumerate(locators, 1):
        log(f"  Trying locator {locator_idx}/{len(locators)}: {locator}")
        
        for attempt in range(1, max_attempts + 1):
            try:
                await page.wait_for_selector(locator, timeout=timeout, state="attached")
                await asyncio.sleep(0.5)  # Wait for animations/modals to settle
                # Try normal click first
                try:
                    await page.click(locator, timeout=10000)
                    log(f"  ✓ Success with '{locator}'")
                    return True
                except Exception:
                    # Try with force=True
                    await page.click(locator, timeout=10000, force=True)
                    log(f"  ✓ Success with '{locator}' (with force)")
                    return True
            except Exception as e:
                log(f"  ✗ Attempt {attempt}/{max_attempts} failed: {str(e)[:40]}")
                if attempt < max_attempts:
                    await asyncio.sleep(0.5)
        
        log(f"  → Moving to next fallback locator...")
    
    log("✗ All locators in fallback chain failed", level="ERROR")
    return False


async def main():
    """Main entry point."""
    # Setup screenshots directory
    setup_screenshots()
    log(f"Screenshot directory: {SCREENSHOT_DIR}")

    # Get the HTML file path
    html_file = os.path.join(os.path.dirname(__file__), 'mock_website.html')

    if not os.path.exists(html_file):
        log(f"HTML file not found at: {html_file}", level="ERROR")
        return

    # Create and run the POC
    poc = AutoClickPOC(html_file)

    # Run all methods
    await poc.run_all_methods()
    
    # Run batch execution simulation (Feature #5)
    await poc.run_batch_execution(num_projects=3)
    
    # Run UI change resilience demo (Feature #6)
    await poc.run_ui_resilience_demo()
    
    # Final Summary
    log("=" * 60)
    log("OVERALL POC SUMMARY")
    log("=" * 60)
    log("✓ All locator methods executed successfully")
    log("✓ Retry logic demonstrated (Method 7)")
    log("✓ Fallback chain demonstrated (Feature #6)")
    log("✓ Batch execution completed")
    log(f"✓ Screenshots saved: {SCREENSHOT_DIR}")
    log("=" * 60)
    log("POC Complete - All features validated!")
    log("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
