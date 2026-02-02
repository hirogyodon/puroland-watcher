import requests, re, json, os

URL = "https://www.puroland.jp/greeting/charaguri_residence/"
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DB_ID = os.environ["NOTION_DB"]

html = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}).text

# Nuxtの初期データを抜き出す
m = re.search(r'window\.__NUXT__\s*=\s*(\{.*?\});', html, re.S)
if not m:
    raise RuntimeError("NUXT data not found")

data = json.loads(m.group(1))

# データの中から日付配列を探す
def find_dates(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "date" and isinstance(v, str) and v.isdigit():
                yield v
            else:
                yield from find_dates(v)
    elif isinstance(obj, list):
        for i in obj:
            yield from find_dates(i)

dates = list(dict.fromkeys(find_dates(data)))
date = dates[-1]

# その日付のキャラ名を探す
def find_names(obj, target):
    if isinstance(obj, dict):
        if obj.get("date") == target and "characters" in obj:
            return [c["name"] for c in obj["characters"]]
        for v in obj.values():
            r = find_names(v, target)
            if r:
                return r
    elif isinstance(obj, list):
        for i in obj:
            r = find_names(i, target)
            if r:
                return r
    return None

names = find_names(data, date)
if not names:
    raise RuntimeError("characters not found")

# Notionへ
url = "https://api.notion.com/v1/pages"
headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}
payload = {
    "parent": {"database_id": DB_ID},
    "properties": {
        "日付": {"title": [{"text": {"content": date}}]},
        "キャラクター": {"rich_text": [{"text": {"content": " / ".join(names)}}]}
    }
}
requests.post(url, headers=headers, json=payload)
