import json
from datetime import datetime
import pytz
import re
from playwright.sync_api import sync_playwright

URLS = {
    "fuku_x": "https://dqx-souba.game-blog.app/item/detail/69eb1ee7cf3b22281bbdb0ed",
    "fuku_y": "https://dqx-souba.game-blog.app/item/detail/6967250f1dc565c0c0137140",
    "fuku_z": "https://dqx-souba.game-blog.app/item/detail/6848bb617d51a045f9b67f69",
}

def get_7day_average(page, url):
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        rows = page.query_selector_all("tr")
        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) >= 2:
                if "7日" in cells[0].inner_text():
                    price_text = cells[1].inner_text().replace(",", "").replace("G", "").strip()
                    if price_text.isdigit():
                        return int(price_text)
        page_text = page.inner_text("body")
        match = re.search(r'7日(?:間の)?平均.*?([\d,]+)', page_text)
        if match:
            return int(match.group(1).replace(",", ""))
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

    prev = existing.get('aucland', {})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        price_x = get_7day_average(page, URLS["fuku_x"])
        price_y = get_7day_average(page, URLS["fuku_y"])
        price_z = get_7day_average(page, URLS["fuku_z"])
        browser.close()

    final_x = price_x if price_x is not None else prev.get('x')
    final_y = price_y if price_y is not None else prev.get('y')
    final_z = price_z if price_z is not None else prev.get('z')

    failed = []
    if price_x is None: failed.append('1等')
    if price_y is None: failed.append('2等')
    if price_z is None: failed.append('3等')

    now = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
    updated_at = now if not failed else f"{now}（取得失敗: {', '.join(failed)}）"

    data = {
        "updated_at": updated_at,
        "aucland": {"x": final_x, "y": final_y, "z": final_z},
        "dwacha":  {"x": 297000, "y": 150000, "z": 80000},
        "dogdra":  existing.get('dogdra')
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    def fmt(v): return f"{v:,}" if v is not None else "取得失敗"
    print(f"ふくびき更新完了: 1等={fmt(final_x)}, 2等={fmt(final_y)}, 3等={fmt(final_z)}")
    if failed:
        print(f"警告: {', '.join(failed)} の取得に失敗。前回値を維持しました。")

if __name__ == "__main__":
    main()
