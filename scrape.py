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
        browser = p.chromium.launch(headless=True)
        # Use a real user agent to help pass basic bot checks
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        url = "https://in.bookmyshow.com/sports/gujarat-titans-vs-royal-challengers-bengaluru-tata-ipl-2026/ET00491081"
        print(f"Checking availability at: {url}")
        
        try:
            # Setting a longer timeout for slow connections in GitHub Actions
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            
            content = page.content()
            
            # Check for price pattern (handles Rs or ₹ and commas)
            price_match = re.search(r'(?:Rs\.?|₹)\s*([\d,]+)\s*onwards', content, re.IGNORECASE)
            
            if price_match:
                price_text = price_match.group(1).replace(',', '')
                try:
                    price = int(price_text)
                    print(f"Found price info: Rs {price} onwards")
                    
                    if price <= 7000:
                        msg = f"📍 TEST ALERT! Tickets are available for Rs {price} (Current limit: 7000)!\nLink: {url}"
                        print("MATCH FOUND!")
                        send_telegram_message(msg)
                    else:
                        print(f"Currently, the cheapest ticket is Rs {price}, which is above 7000 Rs.")
                        # Optional: uncomment to get an update even if price is high
                        # send_telegram_message(f"Status Update: Cheapest ticket is currently Rs {price}.")
                except ValueError:
                    print(f"Could not parse price from text: {price_text}")
            elif "Sold Out" in content:
                print("Status: SOLD OUT")
            else:
                print("Could not detect any price info or 'Sold Out' status. The page might be protected or changed.")
                    
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_availability()