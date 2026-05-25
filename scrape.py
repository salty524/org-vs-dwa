import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import pytz

# 相棒が教えてくれたオーグリードの1等、2等、3等のURLだよ！
URLS = {
    "x": "https://dqx-souba.game-blog.app/item/detail/69eb1ee7cf3b22281bbdb0ed", # 1等コイン
    "y": "https://dqx-souba.game-blog.app/item/detail/6967250f1dc565c0c0137140", # 2等コイン
    "z": "https://dqx-souba.game-blog.app/item/detail/6848bb617d51a045f9b67f69"  # 3等コイン
}

def get_7day_average(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(self, f"エラー：ページが開けなかったよ (Status: {res.status_code})")
            return 0
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 【ししょーの予想ロジック】
        # 表（tr）の中から「7日」という文字が入っている行を探して、その横の数字（価格）を抜き出すよ！
        for tr in soup.find_all('tr'):
            text = tr.get_text()
            if '7日' in text:
                # 行の中から数字だけを強引に抽出するよ（カンマや「G」を取り除く）
                numbers = re.findall(r'\d+', text.replace(',', ''))
                # 「7日」の「7」も拾っちゃうことがあるから、2つ目以降の大きな数字を狙うよ
                for num in numbers:
                    val = int(num)
                    if val > 100: # 100G以上の数字を価格とみなすよ
                        return val

        # もし表で見つからなかったら、ページ全体のテキストから「7日平均」っぽい並びを探す予備ルート！
        page_text = soup.get_text()
        match = re.search(r'7日(?:間の)?平均.*?([\d,]+)', page_text)
        if match:
            return int(match.group(1).replace(',', ''))

    except Exception as e:
        print(f"エラーが発生しちゃった：{e}")
    
    return 0 # 万が一取れなかったら0を返すよ

def main():
    print("相場サイトから7日間の平均値を集めてくるよ！")
    
    # 各URLから価格を取得
    price_x = get_7day_average(URLS["x"])
    price_y = get_7day_average(URLS["y"])
    price_z = get_7day_average(URLS["z"])
    
    # ちゃんと取れたか確認（取れなかったら前回の仮データを入れておく安全弁）
    o_x = price_x if price_x > 0 else 440000
    o_y = price_y if price_y > 0 else 50000
    o_z = price_z if price_z > 0 else 70000

    # データをまとめるよ！ガタラ（ドワチャッカ）は相棒の言う通り固定値だよ！
    prices = {
        "updated_at": datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S'),
        "aucland": {
            "x": o_x,
            "y": o_y,
            "z": o_z
        },
        "dwacha": {
            "x": 297000, # 固定値！
            "y": 150000, # 固定値！
            "z": 80000   # 固定値！
        }
    }
    
    # data.json に保存！
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=4, ensure_ascii=False)
    
    print("データの更新が完了したよ！")
    print(f"オーグリード1等(7日平均): {o_x} G")

if __name__ == "__main__":
    main()