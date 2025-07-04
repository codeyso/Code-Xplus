import lib.util.globalvar as GlobalVar
'''
set_value(name, value)
get_value(name)
add_value(name, value)
'''
# 全局HTTP请求头部
HTTP_HEADER = """
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Upgrade-Insecure-Requests: 1
Cache-Control: max-age=0
Connection: close
"""
# 分割成字典
header_lines = HTTP_HEADER.strip().split('\n')
header = {}
for line in header_lines:
    if ':' in line:
        key, value = line.split(':', 1)
        header[key.strip()] = value.strip()
# 全局HTTP请求头部
GlobalVar.set_value('HTTP_HEADER', header)