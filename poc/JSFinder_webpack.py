# -*- coding:UTF-8 -*-
#api相对根路径
apipath = ''
#js相对根路径
jspath = ''
#过滤后缀
black_suf = ['bcmap', 'vue','svg','css','ts','js','png','js\\']
#修改 header 使其能够在后台运作
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    }
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import node_vm2
import urllib3
import traceback
import re
# 去除错误警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Regular expression comes from https://github.com/GerbenJavado/LinkFinder
# (?:"|')(((?:[a-zA-Z]{1,10}://|//)[^"'/]{1,}\.[a-zA-Z]{2,}[^"']{0,})|((?:/|\.\./|\./)[^"'><,;| *()(%%$^/\\\[\]][^"'><,;|()]{1,})|([a-zA-Z0-9_\-/]{1,}/[a-zA-Z0-9_\-/]{1,}\.(?:[a-zA-Z]{1,4}|action)(?:[\?|/][^"|']{0,}|))|([a-zA-Z0-9_\-]{1,}\.(?:php|asp|aspx|jsp|json|action|html|js|txt|xml)(?:\?[^"|']{0,}|))|((http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?))(?:"|')
class RecoverSpilt():
    def __init__(self):
        self.jsFileNames = []
    def jsCodeCompile(self, jsCode):
        try:
            # 正在处理异步加载代码中
            print('[*] 正在处理异步加载代码中...')
            variable = re.findall(r'\[.*?\]', jsCode)
            if "[" and "]" in variable[0]:
                variable = variable[0].replace("[", "").replace("]", "")
            jsCodeFunc = "function js_compile(%s){js_url=" % (variable) + jsCode + "\nreturn js_url}"
            pattern_jscode = re.compile(r"\(\{\}\[(.*?)\]\|\|.\)", re.DOTALL)
            flag_code = pattern_jscode.findall(jsCodeFunc)
            if flag_code:
                jsCodeFunc = jsCodeFunc.replace("({}[%s]||%s)" % (flag_code[0], flag_code[0]), flag_code[0])
            pattern1 = re.compile(r"\{(.*?)\:")
            pattern2 = re.compile(r"\,(.*?)\:")
            nameList1 = pattern1.findall(jsCode)
            nameList2 = pattern2.findall(jsCode)
            nameList = nameList1 + nameList2
            nameList = list(set(nameList))
            # print("jsCodeFunc = "+ jsCodeFunc)
            with node_vm2.VM() as vm:
                vm.run(jsCodeFunc)
                for name in nameList:
                    if "\"" in name:
                        name = name.replace("\"", "")
                    if "undefined" not in vm.call("js_compile", name):
                        jsFileName = vm.call("js_compile", name)
                        #print('/v2/'+jsFileName)
                        # 追加js根目录
                        #if jspath:
                        #    self.jsFileNames.append(f'/{jspath}/'+jsFileName)
                        #else:
                        #    self.jsFileNames.append('/'+jsFileName)
                        self.jsFileNames.append('/'+jsFileName)
                        #break
            print('[*] 异步JS文件提取成功，提取数量'+str(len(self.jsFileNames)))
        except Exception as e:
            print("[Err] %s" % e)
            print(traceback.format_exc())  # 显示完整的错误信息，包括行数
            return 0

    def checkCodeSpilting(self, jsFilePath, jsFile):
        if "document.createElement(\"script\");" in jsFile:
            print('[*] 疑似存在JS异步加载：'+ jsFilePath)
            pattern = re.compile(r"\w\.p\+\"(.*?)\.js", re.DOTALL)
            if pattern:
                jsCodeList = pattern.findall(jsFile)
                for jsCode in jsCodeList:
                    if len(jsCode) < 30000:
                        jsCode = "\"" + jsCode + ".js\""
                        self.jsCodeCompile(jsCode)

def extract_URL(JS):
    pattern_raw = """
      (?:"|')                               # Start newline delimiter
      (
        ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
        [^"'/]{1,}\.                        # Match a domainname (any character + dot)
        [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
        |
        ((?:/|\.\./|\./)                    # Start with /,../,./
        [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
        [^"'><,;|()]{1,})                   # Rest of the characters can't be
        |
        ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
        [a-zA-Z0-9_\-/]{1,}                 # Resource name
        \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
        (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
        |
        (\w+\/\w+)
        |
        ([a-zA-Z0-9_\-]{1,}                 # filename
        \.(?:php|asp|aspx|jsp|json|
             action|html|js|txt|xml)             # . + extension
        (?:\?[^"|']{0,}|))                  # ? mark with parameters
        |
        ((http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?)
      )
      (?:"|')                               # End newline delimiter
    """
    pattern = re.compile(pattern_raw, re.VERBOSE)
    result = re.finditer(pattern, str(JS))
    if result == None:
        return None
    js_url = []
    return [match.group().strip('"').strip("'") for match in result if match.group() not in js_url]

# GET HTML source
def Extract_html(URL):
    try:
        #后台session请求
        session = requests.Session()
        #verify=False HTTPS请求设置
        raw = session.get(URL, headers=header, timeout=90, verify=False)
        charset = raw.apparent_encoding
        raw = raw.content.decode(charset if charset != None else 'utf-8', "ignore")
        return raw
    except Exception as e:
        print('[-] url请求出错, %s'%type(e))
        return None
    finally:
        session.close()

# Handling relative URLs
def process_url(URL, re_URL):
    # Add some keyword for filter url
    black_url = ["javascript:"]
    # re_URL="js/app.js"
    URL_raw = urlparse(URL)
    # ab_URL="www.baidu.com"
    # 增加一个根路径
    if jspath and re_URL.endswith('.js') and jspath not in re_URL:
       ab_URL = URL_raw.netloc+f'/{jspath}'
    else:
       ab_URL = URL_raw.netloc+''
    # host_URL="https"
    # ab_URL = URL_raw.netloc+''
    host_URL = URL_raw.scheme
    if re_URL[0:2] == "//":
        result = host_URL  + ":" + re_URL
    elif re_URL[0:4] == "http":
        result = re_URL
    elif re_URL[0:2] != "//" and re_URL not in black_url:
        if re_URL[0:1] == "/":
            result = host_URL + "://" + ab_URL + re_URL
        else:
            if re_URL[0:1] == ".":
                if re_URL[0:2] == "..":
                    result = host_URL + "://" + ab_URL + re_URL[2:]
                else:
                    result = host_URL + "://" + ab_URL + re_URL[1:]
            else:
                result = host_URL + "://" + ab_URL + "/" + re_URL
    else:
        result = URL
    return result

def find_last(string,str):
    positions = []
    last_position=-1
    while True:
        position = string.find(str,last_position+1)
        if position == -1:break
        last_position = position
        positions.append(position)
    return positions

def find_by_url(url, js = False):
    script_array = {}
    allurls = []
    if js == False:
        try:
            print("url: " + url)
        except:
            print("Please specify a URL like https://www.baidu.com")
        html_raw = Extract_html(url)
        if html_raw == None: 
            print("Fail to access " + url)
            return None
        html = BeautifulSoup(html_raw, "html.parser")
        # 1、添加 url html里link标签下的href属性到 allurls
        html_links = html.findAll("link")
        for html_link in html_links:
            link_href = html_link.get("href")
            if link_href != None:
                allurls.append(process_url(url, link_href))
        # 增加请求页面
        script_array[url] = html_raw
        # 获取当前页面的script标签
        html_scripts = html.findAll("script")
        for html_script in html_scripts:
            script_src = html_script.get("src")
            #script标签src属性，当前页面通过script标签引入的js地址
            if script_src is not None:
                purl = process_url(url, script_src)
                script_array[purl] = Extract_html(purl)
        i = len(script_array)
        # script_array 字典类型 键是 JS 链接,值是链接返回的 html,在 JS 文件里根据正则匹配结果,然后汇总到 allurls
        for script in script_array:
            temp_urls = extract_URL(script_array[script])
            if len(temp_urls) == 0: 
                i -= 1
                continue
            #1、正则提取js里的地址
            for temp_url in temp_urls:
                allurls.append(process_url(script, temp_url))
            print("Remaining " + str(i) + " | Find " + str(len(temp_urls)) + " URL in " + script)
            i -= 1
        # 提取异步加载的js
        rejslist = []
        for script in script_array:
            rejs = RecoverSpilt()
            rejs.checkCodeSpilting(script, script_array[script])
            rejsfile = rejs.jsFileNames
            for js in rejsfile:
                if js not in rejslist:
                    if jspath:
                        js = f'/{jspath}{js}'
                    url = process_url(script, js)
                    print('[*] 正在提取: %s'%js)
                    html2 = Extract_html(url)
                    temp2_urls = extract_URL(html2)
                    if len(temp2_urls) == 0:
                        continue
                    else:
                        for temp_url in temp2_urls:
                            allurls.append(process_url(script, temp_url))
                    rejslist.append(js)
                else:
                    print('[*] 已经存在: %s'%js)
        result = []
        #过滤后缀
        #black_suf = ['vue','svg','css','gif','js','jpg','png']
        #查找 allurls 中和 url 同根域下的链接, 返回结果为 result 列表
        for singerurl in allurls:
            suf = singerurl[singerurl.rfind('.')+1:]
            if suf in black_suf: continue
            url_raw = urlparse(url)
            domain = url_raw.netloc
            positions = find_last(domain, ".")
            miandomain = domain
            if len(positions) > 1:miandomain = domain[positions[-2] + 1:]
            try:
                suburl = urlparse(singerurl)
            except:
                continue
            subdomain = suburl.netloc
            if miandomain in subdomain or subdomain.strip() == "":
                if singerurl.strip() not in result:
                    result.append(singerurl)
        return result
    return sorted(set(extract_URL(Extract_html(url)))) or None

def find_subdomain(urls, mainurl):
    url_raw = urlparse(mainurl)
    domain = url_raw.netloc
    miandomain = domain
    positions = find_last(domain, ".")
    if len(positions) > 1:miandomain = domain[positions[-2] + 1:]
    subdomains = []
    for url in urls:
        suburl = urlparse(url)
        subdomain = suburl.netloc
        #print(subdomain)
        if subdomain.strip() == "": continue
        if miandomain in subdomain:
            if subdomain not in subdomains:
                subdomains.append(subdomain)
    return subdomains

# 结果输出
def giveresult(urls, domian):
    if urls == None:
        return None
    # 去重排序
    urls = sorted(set(urls))
    # 去重不排序
    # urls = sorted(list(set(urls)), key=urls.index)
    print("\nFind " + str(len(urls)) + " URL:")
    content_subdomain = ""
    global apipath
    for url in urls:
        url2 = urlparse(url)
        if apipath != '':
            apipath = apipath.strip('/')
            #url2 = urlparse(url)
            scheme = url2.scheme
            netloc = url2.netloc
            path = url2.path
            url = scheme+'://'+netloc+'/'+apipath+path
        else:
            url = url2.path
        print(url)
    subdomains = find_subdomain(urls, domian)
    print("\nFind " + str(len(subdomains)) + " Subdomain:")
    for subdomain in subdomains:
        content_subdomain += subdomain + "\n"
        print(subdomain)

print("JSFinder利用说明: 提取目标站点的接口, 当前apipath: {}\n1、获取当前页面script标签src属性的JS, 和script标签自定义的JS, 访问这些JS后用正则提取相关链接\n2、提取当前页面link标签的href\n3、支持webpack异步加载js提取\n4、修改cookies使其能够在后台运作".format(apipath))
def check(**kwargs):
    urls = find_by_url(kwargs['url'])
    #urls = find_by_url(kwargs['url'], urls)
    giveresult(urls, kwargs['url'])

if __name__ == "__main__":
    import os
    #os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8080'
    #os.environ['HTTPS_PROXY'] = 'https://127.0.0.1:8080'
    urls = find_by_url('http://www.baidu.com')
    giveresult(urls, 'http://www.baidu.com')