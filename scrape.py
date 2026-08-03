import json
from datetime import datetime
import pytz
import re
import requests
from bs4 import BeautifulSoup

URLS = {
    "fuku_x": "https://dqx-souba.game-blog.app/item/detail/6a6c1abcdf7f8ffc7562b9d7",
    "fuku_y": "https://dqx-souba.game-blog.app/item/detail/69eb1ee7cf3b22281bbdb0ed",
    "fuku_z": "https://dqx-souba.game-blog.app/item/detail/6967250f1dc565c0c0137140",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xhtml,*/*;q=0.9",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

def get_7day_average(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        if res.status_code != 200:
            print(f"Error: Status code {res.status_code} for {url}")
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
    existing = {}
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            existing = json.load(f)
    except Exception:
        pass

    prev = existing.get('aucland', {})

    price_x = get_7day_average(URLS["fuku_x"])
    price_y = get_7day_average(URLS["fuku_y"])
    price_z = get_7day_average(URLS["fuku_z"])

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
