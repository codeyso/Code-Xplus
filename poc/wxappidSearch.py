# coding:utf-8
import requests
import re
import json
# print('[*]通过appid查询开放搜索的小程序名字')
def check(**kwargs):
    wxappid = kwargs['url']
    url = "https://kainy.cn/api/weapp/info/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh",
    }
    data = f'{{"appid":"{wxappid}"}}'
    r = requests.post(url=url, headers=headers, data=data, timeout=10, verify=False)
    # 解析 JSON 字符串
    data = json.loads(r.text)
    print(json.dumps(data, indent=4, ensure_ascii=False))
    # 将 JSON 对象转换为格式化的字符串
    # formatted_response = json.dumps(data, indent=4, ensure_ascii=False)
    # 打印格式化的响应
    # print(formatted_response)
    return data