import os
import json
from datetime import datetime
import pytz
import re
import requests
from bs4 import BeautifulSoup

URLS = {
    "x": "https://dqx-souba.game-blog.app/item/detail/69eb1ee7cf3b22281bbdb0ed",
    "y": "https://dqx-souba.game-blog.app/item/detail/6967250f1dc565c0c0137140",
    "z": "https://dqx-souba.game-blog.app/item/detail/6848bb617d51a045f9b67f69"
}

def get_7day_average(url):
    api_key = os.environ.get("SCRAPERAPI_KEY")
    if not api_key:
        print("Error: SCRAPERAPI_KEY is not set.")
        return None

    try:
        proxy_url = f"http://api.scraperapi.com?api_key={api_key}&url={url}"
        res = requests.get(proxy_url, timeout=30)
        if res.status_code != 200:
            print(f"Error: Status code {res.status_code}")
            return None

        soup = BeautifulSoup(res.text, 'html.parser')
        for tr in soup.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) >= 2:
                if '7日' in tds[0].get_text():
                    price_text = tds[1].get_text().replace(',', '').replace('G', '').strip()
                    if price_text.isdigit():
                        return int(price_text)

        page_text = soup.get_text()
        match = re.search(r'7日(?:間の)?平均.*?([\d,]+)', page_text)
        if match:
            return int(match.group(1).replace(',', ''))

    except Exception as e:
        print(f"Exception: {e}")

    return None

def main():
    price_x = get_7day_average(URLS["x"])
    price_y = get_7day_average(URLS["y"])
    price_z = get_7day_average(URLS["z"])

    # スクレイプ失敗時は null を入れる（ハードコードのフォールバックなし）
    prices = {
        "updated_at": datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S'),
        "aucland": {"x": price_x, "y": price_y, "z": price_z},
        "dwacha": {"x": 297000, "y": 150000, "z": 80000}
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=4, ensure_ascii=False)

    status_x = f"{price_x:,}" if price_x is not None else "取得失敗"
    status_y = f"{price_y:,}" if price_y is not None else "取得失敗"
    status_z = f"{price_z:,}" if price_z is not None else "取得失敗"
    print(f"Data update completed. (1等: {status_x}, 2等: {status_y}, 3等: {status_z})")

if __name__ == "__main__":
    main()
