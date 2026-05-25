import json
from datetime import datetime
import pytz
import re
import cloudscraper
from bs4 import BeautifulSoup

URLS = {
    "x": "https://dqx-souba.game-blog.app/item/detail/69eb1ee7cf3b22281bbdb0ed",
    "y": "https://dqx-souba.game-blog.app/item/detail/6967250f1dc565c0c0137140",
    "z": "https://dqx-souba.game-blog.app/item/detail/6848bb617d51a045f9b67f69"
}

def get_7day_average(url):
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        res = scraper.get(url, timeout=15)
        if res.status_code != 200:
            print(f"Error: Status code {res.status_code}")
            return 0
        
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
    
    return 0

def main():
    price_x = get_7day_average(URLS["x"])
    price_y = get_7day_average(URLS["y"])
    price_z = get_7day_average(URLS["z"])
    
    o_x = price_x if price_x > 0 else 440000
    o_y = price_y if price_y > 0 else 50000
    o_z = price_z if price_z > 0 else 70000

    prices = {
        "updated_at": datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S'),
        "aucland": {"x": o_x, "y": o_y, "z": o_z},
        "dwacha": {"x": 297000, "y": 150000, "z": 80000}
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=4, ensure_ascii=False)
    
    print(f"Data update completed. (1st: {o_x}, 2nd: {o_y}, 3rd: {o_z})")

if __name__ == "__main__":
    main()
