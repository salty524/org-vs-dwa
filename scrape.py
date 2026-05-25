import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import pytz

URLS = {
    "x": "https://dqx-souba.game-blog.app/item/detail/69eb1ee7cf3b22281bbdb0ed", # 1等
    "y": "https://dqx-souba.game-blog.app/item/detail/6967250f1dc565c0c0137140", # 2等
    "z": "https://dqx-souba.game-blog.app/item/detail/6848bb617d51a045f9b67f69"  # 3等
}

def get_7day_average(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"Error: Status code {res.status_code}")
            return 0
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 表の行（tr）を一つずつループ
        for tr in soup.find_all('tr'):
            tds = tr.find_all('td')
            # セルが2つ以上ある行を対象にする
            if len(tds) >= 2:
                # 1つ目のセルに「7日」という文字が含まれている場合
                if '7日' in tds[0].get_text():
                    # 2つ目のセル（価格側）のテキストを取得して、カンマやGや空白を削除
                    price_text = tds[1].get_text().replace(',', '').replace('G', '').strip()
                    # 数字だけの文字列になっていたら整数に変換して返す
                    if price_text.isdigit():
                        return int(price_text)

    except Exception as e:
        print(f"Exception: {e}")
    
    return 0

def main():
    price_x = get_7day_average(URLS["x"])
    price_y = get_7day_average(URLS["y"])
    price_z = get_7day_average(URLS["z"])
    
    # データが取得できなかった場合のみ、デフォルト値を適用
    o_x = price_x if price_x > 0 else 440000
    o_y = price_y if price_y > 0 else 50000
    o_z = price_z if price_z > 0 else 70000

    prices = {
        "updated_at": datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S'),
        "aucland": {
            "x": o_x,
            "y": o_y,
            "z": o_z
        },
        "dwacha": {
            "x": 297000,
            "y": 150000,
            "z": 80000
        }
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=4, ensure_ascii=False)
    
    print("Data update completed.")
    print(f"Current Results -> 1st: {o_x}, 2nd: {o_y}, 3rd: {o_z}")

if __name__ == "__main__":
    main()
