import re
import os
import sys
import urllib.request
import urllib.parse
from playwright.sync_api import sync_playwright

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Telegram notification skipped: Environment variables not set.")
        return

    print(f"Sending Telegram notification: {message}")
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
        with urllib.request.urlopen(url, data=data) as response:
            if response.status == 200:
                print("Telegram message sent successfully!")
            else:
                print(f"Failed to send Telegram message. Status: {response.status}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def check_availability():
    with sync_playwright() as p:
        # Launching with more "human" arguments
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        
        # Add a custom script to further hide automation
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()
        url = "https://in.bookmyshow.com/sports/gujarat-titans-vs-royal-challengers-bengaluru-tata-ipl-2026/ET00491081"
        print(f"Checking availability at: {url}")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(10000) # Wait 10 seconds for Cloudflare to settle
            
            # Save a debug screenshot for GitHub Actions
            page.screenshot(path="debug_screenshot.png")
            print("Debug screenshot saved.")
            
            content = page.content()
            
            # Check for Cloudflare challenge markers
            if "Attention Required" in content or "cf-challenge" in content:
                print("DETECTED: Cloudflare Bot Protection is blocking the request.")
                return

            # Check for price pattern
            price_match = re.search(r'(?:Rs\.?|₹)\s*([\d,]+)\s*onwards', content, re.IGNORECASE)
            
            if price_match:
                price_text = price_match.group(1).replace(',', '')
                try:
                    price = int(price_text)
                    print(f"Found price info: Rs {price} onwards")
                    
                    if price <= 3100:
                        msg = f"📍 TICKET ALERT! Tickets are available for Rs {price} (Limit: 3100)!\nLink: {url}"
                        print("MATCH FOUND!")
                        send_telegram_message(msg)
                    else:
                        print(f"Currently, the cheapest ticket is Rs {price}, which is above 3100 Rs.")
                except ValueError:
                    print(f"Could not parse price from text: {price_text}")
            elif "Sold Out" in content:
                print("Status: SOLD OUT")
            else:
                print("Could not detect any price info. Inspect the debug_screenshot.png in GitHub Actions artifacts.")
                    
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_availability()