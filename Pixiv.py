"""
P站小爬虫 爬每日排行榜
环境需求：Python3.6+ / Redis
项目地址：https://github.com/nyaasuki/PixivSpider

"""

import re
import os

try:
    import json
    import configparser
    import sqlite3
    import requests

except:
    print('检测到缺少必要包！正在尝试安装！.....')
    os.system(r'pip install -r requirements.txt')
    import json
    import configparser
    import sqlite3
    import requests

requests.packages.urllib3.disable_warnings()
file_path = "cookie.txt"

class PixivDatabase:
    def __init__(self, db_file="pixiv_spider.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS pixiv_data (
            illust_id TEXT PRIMARY KEY,
            user_id TEXT
        )
        """)
        self.conn.commit()

    def get(self, illust_id):
        self.cursor.execute("SELECT user_id FROM pixiv_data WHERE illust_id = ?", (illust_id,))
        result = self.cursor.fetchone()
        return result

    def save(self, illust_id, user_id):
        if not self.get(illust_id):
            self.cursor.execute("INSERT INTO pixiv_data (illust_id, user_id) VALUES (?, ?)", (illust_id, user_id))
            self.conn.commit()
        else:
            print(f"插画ID: {illust_id} 已存在，跳过保存")

class PixivSpider:
    def __init__(self, proxy=None, config_file='config.ini'):
        self.db = PixivDatabase()
        self.config = self.load_config(config_file)
        self.proxy = proxy if proxy else self.get_proxy(config_file)
        self.ajax_url = 'https://www.pixiv.net/ajax/illust/{}/pages'
        self.mode = self.config.get('ranking', 'mode')
        self.top_url = f'https://www.pixiv.net/ranking.php?mode={self.mode}'
        self.headers = {}

    def load_config(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

    def get_proxy(self, config_file='config.ini'):
        config = self.load_config(config_file)
        proxy = config.get('proxy', 'http')
        return {'http': proxy, 'https': proxy}

    def get_top_url(self, num):
        params = {'mode': self.mode, 'content': 'illust', 'p': f'{num}', 'format': 'json'}
        response = requests.get(self.top_url, params=params, headers=self.headers, proxies=self.proxy, verify=False)
        json_data = response.json()
        
        if 'error' in json_data and json_data['error']:
            print(f"第 {num} 页出现错误：{json_data['error']}")
            return

        if 'contents' in json_data:
            self.process_top_pics(json_data['contents'])
        else:
            print(f"第 {num} 页没有找到有效内容！")

    def process_top_pics(self, data):
        for url in data:
            illust_id = url['illust_id']
            illust_user = url['user_id']

            if not self.db.get(illust_id):
                if self.get_list(illust_id):
                    self.db.save(illust_id, illust_user)
            else:
                print(f"插画ID: {illust_id} 已存在，跳过该插画")

    def get_list(self, illust_id):
        response = requests.get(self.ajax_url.format(illust_id), headers=self.headers, proxies=self.proxy, verify=False)
        json_data = response.json()

        if 'error' in json_data and json_data['error'] == True:
            print(f"获取插画ID: {illust_id} 时出现错误：{json_data['error']}")
            return True

        for l in json_data.get('body', []):
            if 'urls' not in l or 'original' not in l['urls']:
                print(f"跳过，图片链接不存在：{l}")
                continue

            url_temp = l['urls']['original']

            if not self.db.get(illust_id):
                if self.download_image(url_temp, illust_id):
                    self.db.save(illust_id, l.get('user_id'))
            else:
                print(f"插画ID: {illust_id} 已存在，跳过该插画")
                break

        return False

    def download_image(self, url, illust_id):
        file_name = re.findall(r'/\d+/\d+/\d+/\d+/\d+/\d+/(.*)', url)[0]
        file_path = f'./img/{file_name}'

        if os.path.exists(file_path):
            print(f'文件：{file_name} 已存在，跳过')
            return True
        if not os.path.exists('./img'):
            os.makedirs('./img')

        print(f'开始下载：{file_name}')
        for _ in range(3):  # 尝试三次下载
            try:
                img_temp = requests.get(url, headers=self.headers, proxies=self.proxy, timeout=15, verify=False)
                if img_temp.status_code == 200:
                    with open(file_path, 'wb') as fp:
                        fp.write(img_temp.content)
                    return True
                else:
                    print(f"下载失败，HTTP状态码：{img_temp.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"下载错误: {e}，重试")
        return False

    def pixiv_main(self):
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                cookie = file.read().strip()
        else:
            while True:
                cookie = input("请输入cookie：").strip()
                if cookie:
                    with open(file_path, "w") as file:
                        file.write(cookie)
                    break
                else:
                    print("输入不能为空，请重新输入。")

        self.headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6',
            'dnt': '1',
            'cookie': f'{cookie}',
            'referer': 'https://www.pixiv.net/',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
        }

        for page_num in range(1, 11):
            self.get_top_url(page_num)

if __name__ == '__main__':
    spider = PixivSpider()
    spider.pixiv_main()
