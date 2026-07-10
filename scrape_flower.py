import json
from datetime import datetime
import pytz
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xhtml,*/*;q=0.9",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

FLOWERS = [
    # 便利ツールふくびき group1: 便利ツール + トルネコ + フラワーギフト券
    {"name": "カナリヤダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dd9c", "cats": ["便利ツール", "トルネコ", "フラワーギフト券"]},
    {"name": "アンバーダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dd9d", "cats": ["便利ツール", "トルネコ", "フラワーギフト券"]},
    {"name": "ベビーピンクダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dd9e", "cats": ["便利ツール", "トルネコ", "フラワーギフト券"]},
    {"name": "あおりんごダリア",     "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dd9f", "cats": ["便利ツール", "トルネコ", "フラワーギフト券"]},
    {"name": "レモンダリア",         "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dda0", "cats": ["便利ツール", "トルネコ", "フラワーギフト券"]},
    {"name": "ミントダリア",         "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dda1", "cats": ["便利ツール", "トルネコ", "フラワーギフト券"]},
    {"name": "シーグリーンダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dda2", "cats": ["便利ツール", "トルネコ", "フラワーギフト券"]},
    {"name": "しらあいダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dda3", "cats": ["便利ツール", "トルネコ", "フラワーギフト券"]},
    {"name": "しゅいろダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dda4", "cats": ["便利ツール", "トルネコ", "フラワーギフト券"]},
    {"name": "ふじいろダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dda5", "cats": ["便利ツール", "トルネコ", "フラワーギフト券"]},
    # 便利ツールふくびき group2: 便利ツール + トルネコ
    {"name": "あまいろダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddb8", "cats": ["便利ツール", "トルネコ"]},
    {"name": "こげちゃダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddb9", "cats": ["便利ツール", "トルネコ"]},
    {"name": "あかねダリア",         "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddba", "cats": ["便利ツール", "トルネコ"]},
    {"name": "みかんダリア",         "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddbb", "cats": ["便利ツール", "トルネコ"]},
    {"name": "のうこんダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddbc", "cats": ["便利ツール", "トルネコ"]},
    {"name": "うぐいすダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddbd", "cats": ["便利ツール", "トルネコ"]},
    {"name": "ろくしょうダリア",     "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddbe", "cats": ["便利ツール", "トルネコ"]},
    {"name": "うすあいダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddbf", "cats": ["便利ツール", "トルネコ"]},
    {"name": "きぞくねずダリア",     "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddc0", "cats": ["便利ツール", "トルネコ"]},
    {"name": "むらさきダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddc1", "cats": ["便利ツール", "トルネコ"]},
    # 便利ツールふくびき group3: 便利ツールのみ
    {"name": "アイビーダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/68241910bc07819a62421c17", "cats": ["便利ツール"]},
    {"name": "きみどりダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/68241910bc07819a62421c18", "cats": ["便利ツール"]},
    {"name": "ライトイエロダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/68241911bc07819a62421c19", "cats": ["便利ツール"]},
    {"name": "やまぶきダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/68241911bc07819a62421c1a", "cats": ["便利ツール"]},
    {"name": "トマトダリア",         "url": "https://dqx-souba.game-blog.app/item/detail/68241912bc07819a62421c1b", "cats": ["便利ツール"]},
    {"name": "ホットピンクダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/68241912bc07819a62421c1c", "cats": ["便利ツール"]},
    {"name": "みずいろダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/68241913bc07819a62421c1d", "cats": ["便利ツール"]},
    {"name": "ゼニスブルーダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/68241913bc07819a62421c1e", "cats": ["便利ツール"]},
    {"name": "グレープダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/68241914bc07819a62421c1f", "cats": ["便利ツール"]},
    {"name": "フォグブルーダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/68241914bc07819a62421c20", "cats": ["便利ツール"]},
    # スペシャルふくびき: スペシャル + トルネコ + フラワーギフト券Ⅱ
    {"name": "カスタードダリア",     "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dda6", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "ふかみどりダリア",     "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dda7", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "しろはなだダリア",     "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dda8", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "ダークブルーダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67dda9", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "ピュアブルーダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddaa", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "パープルダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddab", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "マゼンタダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddac", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "うめねずダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddad", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "しらふじいろダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddae", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "うすざくらダリア",     "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddaf", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "ルビーダリア",         "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddb0", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "ガーネットダリア",     "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddb1", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "コルクダリア",         "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddb2", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "ライトグレーダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddb3", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "アッシュダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddb4", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "ローズグレーダリア",   "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddb5", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "スチールダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddb6", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
    {"name": "しっこくダリア",       "url": "https://dqx-souba.game-blog.app/item/detail/636e62ea1807614fdf67ddb7", "cats": ["スペシャル", "トルネコ", "フラワーギフト券Ⅱ"]},
]

def get_7day_average(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        if res.status_code != 200:
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

    prev_items = {}
    if existing.get('flower') and existing['flower'].get('items'):
        for item in existing['flower']['items']:
            prev_items[item['name']] = item.get('price')

    results = []
    failed = []
    for i, flower in enumerate(FLOWERS):
        print(f"[{i+1}/{len(FLOWERS)}] {flower['name']} を取得中...")
        price = get_7day_average(flower['url'])
        if price is None:
            price = prev_items.get(flower['name'])
            if price is None:
                failed.append(flower['name'])
            else:
                print(f"  → 取得失敗。前回値 {price:,} を維持")
        else:
            print(f"  → {price:,} G")
        results.append({
            "name": flower['name'],
            "url":  flower['url'],
            "cats": flower['cats'],
            "price": price
        })

    now = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
    updated_at = now if not failed else f"{now}（取得失敗: {len(failed)}件）"

    existing['flower'] = {
        "updated_at": updated_at,
        "items": results
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)

    print(f"\nフラワー相場更新完了: {len(results) - len(failed)}/{len(results)} 件取得成功")
    if failed:
        print(f"取得失敗: {', '.join(failed)}")

if __name__ == "__main__":
    main()
