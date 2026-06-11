import os
import json
from datetime import datetime
import pytz
import re
import requests
from bs4 import BeautifulSoup

URLS = {
    "cell":  "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dd4b",
    "shard": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dd4a",
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
    price_cell  = get_7day_average(URLS["cell"])
    price_shard = get_7day_average(URLS["shard"])

    # 既存のdata.jsonを読み込んでdogdraセクションだけ上書き
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}

    data['dogdra'] = {"cell": price_cell, "shard": price_shard}

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    def fmt(v): return f"{v:,}" if v is not None else "取得失敗"
    print(f"ドグドラ更新完了: 魔因細胞={fmt(price_cell)}, 輝晶の砕片={fmt(price_shard)}")

if __name__ == "__main__":
    main()
