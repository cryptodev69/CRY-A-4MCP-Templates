import asyncio
from playwright.async_api import Playwright, async_playwright, expect

async def run():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto("http://localhost:3000/crawlers")
            print("Navigated to crawlers page.")

            # Click the 'Create Crawler' button
            create_crawler_button = page.locator('button:has-text("Create Crawler")')
            await expect(create_crawler_button).to_be_visible()
            await create_crawler_button.click()
            print("Clicked 'Create Crawler' button.")

            # Wait for the modal to appear and then the dropdown button within it
            dropdown_button = page.locator('button[type="button"].w-full.px-4.py-3.text-left.border.rounded-xl')
            await expect(dropdown_button).to_be_visible(timeout=10000)
            await dropdown_button.click()
            print("Clicked URL Mapping dropdown button.")

            # Wait for the dropdown panel to be visible
            dropdown_panel = page.locator('div.absolute.z-50.w-full.mt-2.bg-white')
            await expect(dropdown_panel).to_be_visible(timeout=10000)
            print("Dropdown panel is visible.")

            # Check if the dropdown list is empty
            options = await dropdown_panel.locator('button.w-full.p-4.text-left').all()
            if not options:
                print("The URL mapping dropdown list is empty.")
            else:
                print(f"The URL mapping dropdown list contains {len(options)} options.")
                for i, option in enumerate(options):
                    text = await option.text_content()
                    print(f"  Option {i+1}: {text.strip()}")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run())