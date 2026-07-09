import json
from datetime import datetime
import pytz
from playwright.sync_api import sync_playwright

URLS = {
    "fuku_x": "https://dqx-souba.game-blog.app/item/detail/69eb1ee7cf3b22281bbdb0ed",
    "fuku_y": "https://dqx-souba.game-blog.app/item/detail/6967250f1dc565c0c0137140",
    "fuku_z": "https://dqx-souba.game-blog.app/item/detail/6848bb617d51a045f9b67f69",
}

def get_7day_average(page, url):
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        print(page.content()[:3000])
    except Exception as e:
        print(f"Exception: {e}")
    return None

def main():
    existing = {}
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            existing = json.load(f)
    except Exception:
        pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # 1URLだけ試す
        get_7day_average(page, URLS["fuku_x"])
        browser.close()

if __name__ == "__main__":
    main()
