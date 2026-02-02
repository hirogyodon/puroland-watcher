import requests, re, os

URL = "https://www.puroland.jp/greeting/charaguri_residence/"
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DB_ID = os.environ["NOTION_DB"]

# 一番下の日付を取得
html = requests.get(URL).text
dates = re.findall(r'<option[^>]*value="(\d+)"', html)
date = dates[-1]

# その日付のページを取得
html2 = requests.get(URL + "?date=" + date).text
names = re.findall(r'p-greeting-residence__name">([^<]+)', html2)

# Notionへ保存
url = "https://api.notion.com/v1/pages"
headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

payload = {
    "parent": {"database_id": DB_ID},
    "properties": {
        "日付": {
            "title": [{"text": {"content": date}}]
        },
        "キャラクター": {
            "rich_text": [{"text": {"content": " / ".join(names)}}]
        }
    }
}

requests.post(url, headers=headers, json=payload)
