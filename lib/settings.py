# -*- coding: utf-8 -*-
from tkinter import StringVar, IntVar
import os
import sys
# 当前python.exe执行路径
PojectPath = os.path.dirname(os.path.realpath(sys.executable))
# 获取项目根据路径
rootPath = os.getcwd()
# 项目根路径
basepath = os.getcwd().replace('\\', '/')
# 中文主题名称映射
theme_names = {
    'winnative': 'Windows 原生',
    'xpnative': 'XP 原生',
    'clam': '清淡',
    'alt': '替代',
    'default': '默认',
    'classic': '经典',
    'vista': 'Vista',
}
#代理界面_Proxy
Proxy_type = StringVar(value='HTTP/HTTPS')#代理界面_代理类型_HTTP
Proxy_CheckVar1 = IntVar()#代理界面_控制代理开关1
Proxy_CheckVar2 = IntVar()#代理界面_控制代理开关0
Proxy_addr = StringVar(value='127.0.0.1')#代理界面_代理IP
Proxy_port = StringVar(value='8080')#代理界面_代理端口
Proxy_user = StringVar(value='')#代理界面_账号
Proxy_pwd = StringVar(value='')#代理界面_密码
Proxy_url = StringVar(value='http://example.com')#代理界面_测试站点
Proxy_timeout = StringVar(value='5')#代理界面_超时时间
#漏洞扫描界面_A
Ent_A_Top_thread = StringVar(value='10')#漏洞扫描界面_顶部_线程_10
Ent_A_Top_Text = '''
_________            .___               ____  ___      .__                
\_   ___ \  ____   __| _/____           \   \/  /_____ |  |  __ __  ______
/    \  \/ /  _ \ / __ |/ __ \   ______  \     /\____ \|  | |  |  \/  ___/
\     \___(  <_> ) /_/ \  ___/  /_____/  /     \|  |_> >  |_|  |  /\___ \ 
 \______  /\____/\____ |\___  >         /___/\  \   __/|____/____//____  >
        \/            \/    \/                \_/__|                   \/ 
v0.20250704
'''

# 爬取代理的页数
Proxy_page = IntVar(value=1)
# 爬取代理的页数
Proxy_webtitle = StringVar(value='米扑代理')
Proxy_web = {
    '米扑代理' : 'freeProxy01',
    '66代理' : 'freeProxy02',
    'pzzqz' : 'freeProxy03',
    '神鸡代理' : 'freeProxy04',
    '快代理' : 'freeProxy05',
    '极速代理' : 'freeProxy06',
    '云代理' : 'freeProxy07',
    '小幻代理' : 'freeProxy08',
    '免费代理库' : 'freeProxy09',
    '89免费代理' : 'freeProxy13',
    '西拉代理' : 'freeProxy14',
    'proxy-list' : 'freeProxy15',
    'proxylistplus' : 'freeProxy16',
    'FOFA' : 'FOFApi',
    'Hunter': 'HunterApi',
    '360Quake': 'QuakeApi',
    'ZoomEye': 'ZoomEyeApi',
}
#代理变量
variable_dict = {
    "Proxy_CheckVar1" : Proxy_CheckVar1,
    "Proxy_CheckVar2" : Proxy_CheckVar2,
    "PROXY_TYPE" : Proxy_type,
    "Proxy_addr" : Proxy_addr,
    "Proxy_user" : Proxy_user,
    "Proxy_pwd" : Proxy_pwd,
    "Proxy_port" : Proxy_port,
    "Proxy_page" : Proxy_page,
    "Proxy_webtitle" : Proxy_webtitle,
    "Proxy_url": Proxy_url,
    "Proxy_timeout": Proxy_timeout,
}