# -*- coding: utf-8 -*-
from tkinter import Toplevel,Menu,Frame,scrolledtext
from tkinter.filedialog import askopenfilename
from tkinter import BOTH,INSERT
from numpy import sort
import ipaddress
import base64
import os
import re
import chardet
import lib.util.globalvar as GlobalVar
# 加载多目标类
class Loadfile():
    def __init__(self, gui):
        self.file = Toplevel(gui.root)
        # 在创建时隐藏窗口
        self.file.withdraw()
        self.file.title("多目标输入界面")
        self.file.geometry('700x400+650+150')
        self.file.iconbitmap('python.ico')

        # 顶级菜单
        self.menubar = Menu(self.file)
        self.menubar.add_command(label = "导 入", command=self.openfile)
        self.menubar.add_command(label = "清 空", command=self.clearfile)
        self.menubar.add_command(label = "添加http", command=self.addhttp)
        self.menubar.add_command(label = "添加https", command=self.addhttps)
        self.menubar.add_command(label = "CIDR", command=self.summarize_ips)
        self.menubar.add_command(label = "hex编码(GBK)", command=self.hex_gb2312)
        self.menubar.add_command(label = "去重", command=self.del_same)
        self.menubar.add_command(label = "截取后6位", command=self.split_str)
        self.menubar.add_command(label = "长字符格式化", command=self.format_long_string)

        # 显示菜单
        self.file.config(menu = self.menubar)
        self.frmA = Frame(self.file, width=650, height=400,bg="white")
        self.frmA.pack(expand=1, fill=BOTH)
        self.TexA = scrolledtext.ScrolledText(self.frmA, font=("consolas", 10), width=74, height=19, undo = True)
        self.TexA.pack(expand=1, fill=BOTH)
        GlobalVar.set_value('myurlsTexA', self.TexA)
        # 关联回调函数
        self.file.protocol("WM_DELETE_WINDOW", self.close)
        GlobalVar.set_value('myurls', self)

    def hide(self):
        """
        隐藏界面
        """
        self.file.withdraw()
        
    def show(self):
        """
        显示界面
        """
        self.file.update()
        self.file.deiconify()
        
    def close(self):
        """
        关闭界面
        """
        self.hide()
        
    def openfile(self):
        default_dir = r"./"
        file_path = askopenfilename(title=u'选择文件', initialdir=(os.path.expanduser(default_dir)))
        if file_path == '':
            return
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                array = f.readlines()
                self.clearfile()
                for i in array:
                    self.TexA.insert(INSERT, i.replace(' ',''))
        except Exception as e:
            pass
        
    def clearfile(self):
        self.TexA.delete('1.0','end')

    def addhttp(self):
        Loadfile_text = self.TexA.get('0.0','end')
        self.TexA.delete('1.0','end')
        array = Loadfile_text.split("\n")
        array = [i for i in array if i!='']
        #print(array)
        index = 1
        for i in array:
            i = 'http://'+i.replace('http://','').replace('https://','')
            if index == len(array):
                self.TexA.insert(INSERT, i)
            else:
                self.TexA.insert(INSERT, i+'\n')
            index = index+1

    def addhttps(self):
        Loadfile_text = self.TexA.get('0.0','end')
        self.TexA.delete('1.0','end')
        array = Loadfile_text.split("\n")
        array = [i for i in array if i!='']
        #print(array)
        index = 1
        for i in array:
            i = 'https://'+i.replace('http://','').replace('https://','')
            if index == len(array):
                self.TexA.insert(INSERT, i)
            else:
                self.TexA.insert(INSERT, i+'\n')
            index = index+1

    def hex_gb2312(self):
        Loadfile_text = self.TexA.get('0.0','end').strip('').strip('\n').strip('\r\n')
        self.TexA.delete('1.0','end')
        # 编码为GB2312格式的字节串
        encoded_bytes = Loadfile_text.encode('gb2312')
        hex_encoded = encoded_bytes.hex()
        # 将字节串转换为十六进制表示形式
        self.TexA.insert(INSERT, hex_encoded)

    def fofa(self):
        Loadfile_text = self.TexA.get('0.0','end')
        array = Loadfile_text.split("\n")
        array = [i for i in array if i!='']
        pre = '('
        suf = ')'
        template = 'host="%s"'
        fofa_list = []
        for i in array:
            fofa_list.append(template%i)
        fofastr = pre+'||'.join(fofa_list)+suf
        hunterstr = fofastr.replace('host', 'domain')
        print(fofastr)
        print(hunterstr)

    def de_base64(self):
        Loadfile_text = self.TexA.get('0.0','end')
        self.TexA.delete('1.0','end')
        array = Loadfile_text.split("\n")
        array = [i for i in array if i!='']
        #print(array)
        index = 1
        for i in array:
            try:
                result = base64.b64decode(i).decode()
            except Exception as e:
                result = '[-]解密失败: '+ i
            finally:
                if index == len(array):
                    self.TexA.insert(INSERT, result)
                else:
                    self.TexA.insert(INSERT, result+'\n')
                index = index+1

    def del_same(self):
        Loadfile_text = self.TexA.get('0.0','end')
        self.TexA.delete('1.0','end')
        array = Loadfile_text.split("\n")
        array = [i for i in array if i!='']
        array = sort(list(set(array)))
        index = 1
        for i in array:
            if index == len(array):
                self.TexA.insert(INSERT, i)
            else:
                self.TexA.insert(INSERT, i+'\n')
            index = index+1


    def split_null(self):
        Loadfile_text = self.TexA.get('0.0','end')
        self.TexA.delete('1.0','end')
        array = Loadfile_text.split("\n")
        array = [i for i in array if i!='']
        #print(array)
        index = 1
        for i in array:
            try:
                result = i.split()[0]
            except Exception as e:
                pass
            finally:
                if index == len(array):
                    self.TexA.insert(INSERT, result)
                else:
                    self.TexA.insert(INSERT, result+'\n')
                index = index+1

    # ip地址列表，整理成CIDR地址段
    def summarize_ips(self):
        try:
            Loadfile_text = self.TexA.get('0.0','end')
            ip_list = Loadfile_text.split("\n")
            ip_list = [i for i in ip_list if i!='']
            ip_networks = [ipaddress.ip_network(ip) for ip in ip_list]
            aggregated_networks = ipaddress.collapse_addresses(ip_networks)
            cidr_list = [str(network) for network in aggregated_networks]
            for ip in cidr_list:
                print(ip)
        except Exception as e:
            print(str(e))

    def format_long_string(self):
        long_string = self.TexA.get('0.0','end').strip('\n')
        self.TexA.delete('1.0','end')
        var_name = 'data'
        # 按照固定长度（此处为80）将字符串分割成多行
        lines = [long_string[i:i+80] for i in range(0, len(long_string), 80)]

        # 使用反斜杠换行符连接字符串，并添加前缀 r 以避免对特殊字符进行转义
        formatted_lines = [f"{var_name}=r\"{lines[0]}\" \\"]
        for line in lines[1:]:
            formatted_lines.append(f"{' '*len(var_name)}r\"{line}\" \\")
        formatted_string = '\n'.join(formatted_lines)

        # 返回格式化后的字符串
        self.TexA.insert(INSERT, formatted_string)

    def remove_status(self):
        Loadfile_text = self.TexA.get('0.0','end')
        self.TexA.delete('1.0','end')
        array = Loadfile_text.split("\n")
        array = [i for i in array if i!='']
        #print(array)
        index = 1
        for i in array:
            try:
                i = i.replace(re.search(r'[0-9]{3}$',i).group(), '')
            except Exception:
                pass
            if index == len(array):
                self.TexA.insert(INSERT, i)
            else:
                self.TexA.insert(INSERT, i+'\n')
            index = index+1

    def Resolve_IP(self):
        from ipaddress import ip_network
        Loadfile_text = self.TexA.get('0.0','end')
        self.TexA.delete('1.0','end')
        array = Loadfile_text.split("\n")
        array = [i for i in array if i!='']
        for i in array:
            try:
                network = ip_network(i, strict=False)
                for host in network.hosts():
                    self.TexA.insert(INSERT, host.exploded+'\n')
            except:
                continue

    def split_str(self):
        Loadfile_text = self.TexA.get('0.0','end')
        self.TexA.delete('1.0','end')
        array = Loadfile_text.split("\n")
        array = [i for i in array if i!='']
        for i in array:
            try:
                self.TexA.insert(INSERT, i[-6:]+'\n')
            except:
                continue

    def split_result(self):
        Loadfile_text = self.TexA.get('0.0','end')
        self.TexA.delete('1.0','end')
        array = Loadfile_text.split("\n")
        array = [i for i in array if i!='']
        for result in array:
            try:
                target = result.split(' ')[1]
                self.TexA.insert(INSERT, str(target)+'\n')
            except Exception as e:
                self.TexA.insert(INSERT, str(e))

def get_encoding(file):
    # 二进制方式读取，获取字节数据，检测类型
    with open(file, 'rb') as f:
        data = f.read()
        return chardet.detect(data)['encoding']

def get_encode_info(file):
    with open(file, 'rb') as f:
        data = f.read()
        result = chardet.detect(data)
        return result['encoding']

def read_file(file):
    with open(file, 'rb') as f:
        return f.read()

def write_file(content, file):
    with open(file, 'wb') as f:
        f.write(content)

def convert_encode2utf8(file, original_encode, des_encode):
    file_content = read_file(file)
    file_decode = file_content.decode(original_encode, 'ignore')
    file_encode = file_decode.encode(des_encode)
    write_file(file_encode, file)