# -*- coding: utf-8 -*-
import random,binascii,subprocess,sys,os,webbrowser
import lib.util.globalvar as GlobalVar
import tkinter as tk
import hashlib
import threading
import types
import copy
import sqlite3

from tkinter import END,ttk,X
# from Crypto.Cipher import DES
# from urllib import request

class AttribDict(dict):
    """
    This class defines the dictionary with added capability to access members as attributes
    """

    def __init__(self, indict=None, attribute=None):
        if indict is None:
            indict = {}

        # Set any attributes here - before initialisation
        # these remain as normal attributes
        self.attribute = attribute
        dict.__init__(self, indict)
        self.__initialised = True

        # After initialisation, setting attributes
        # is the same as setting an item

    def __getattr__(self, item):
        """
        Maps values to attributes
        Only called if there *is NOT* an attribute with this name
        """

        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError("unable to access item '%s'" % item)

    def __setattr__(self, item, value):
        """
        Maps attributes to values
        Only if we are initialised
        """

        # This test allows attributes to be set in the __init__ method
        if "_AttribDict__initialised" not in self.__dict__:
            return dict.__setattr__(self, item, value)

        # Any normal attributes are handled normally
        elif item in self.__dict__:
            dict.__setattr__(self, item, value)

        else:
            self.__setitem__(item, value)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dict):
        self.__dict__ = dict

    def __deepcopy__(self, memo):
        retVal = self.__class__()
        memo[id(self)] = retVal

        for attr in dir(self):
            if not attr.startswith('_'):
                value = getattr(self, attr)
                if not isinstance(value, (types.BuiltinFunctionType, types.FunctionType, types.MethodType)):
                    setattr(retVal, attr, copy.deepcopy(value, memo))

        for key, value in self.items():
            retVal.__setitem__(key, copy.deepcopy(value, memo))

        return retVal

# input
class CustomInputHandler:
    input_buffer = ""
    # 添加一个实例变量
    input_var = None

    @staticmethod
    def input(prompt=">>> "):
        text_widget = GlobalVar.get_value("gui").TexB
        text_widget.configure(state="normal")
        # 获取焦点
        text_widget.focus_set()
        # 插入白色字符
        text_widget.insert(tk.END, prompt, ('white',))
        text_widget.see(tk.END)
        text_widget.update()
        # 绑定按键事件
        text_widget.bind("<Key>", CustomInputHandler.handle_key)
        # 实例化 input_var
        CustomInputHandler.input_var = tk.IntVar()
        # 暂停程序的执行，直到指定的变量被设置为非零值。
        # 等待用户在文本框中输入并按下回车键后设置 input_var 变量的值。
        text_widget.wait_variable(CustomInputHandler.input_var)
        # 解绑按键事件
        text_widget.unbind("<Key>")
        input_text = CustomInputHandler.input_buffer
        CustomInputHandler.input_buffer = ""
        text_widget.configure(state="normal")
        # 插入换行符
        text_widget.insert(tk.END, '\n')
        text_widget.configure(state="disabled")
        # 去除 prompt
        if input_text.startswith(prompt):
            input_text = input_text[len(prompt):]
        return input_text

    @staticmethod
    def handle_key(event):
        text_widget = GlobalVar.get_value("gui").TexB
        if event.char.isprintable():
            # 如果是字符，设置当前插入字符的样式为白色
            text_widget.configure(state="normal")
            text_widget.insert(tk.END, event.char, ('white',))
            text_widget.configure(state="disabled")

        elif event.keysym == "Return":
            CustomInputHandler.input_buffer = text_widget.get("end-1c linestart", tk.END).strip()
            # 通知 wait_variable 方法，即用户已经按下回车键，可以解除阻塞，程序继续执行。
            CustomInputHandler.input_var.set(1)

#重定向输出类
#from lib.settings import echo_threadLock
echo_threadLock = threading.Lock()
class TextRedirector(object):
    #global echo_threadLock
    def __init__(self, widget, type="stdout", index="poc"):
        #同步锁
        self.widget = widget
        self.type = type
        self.index = index
        #颜色定义
        self.widget.tag_config("red", foreground="red")
        self.widget.tag_config("white", foreground="white")
        self.widget.tag_config("green", foreground="green")
        self.widget.tag_config("black", foreground="black")
        self.widget.tag_config("yellow", foreground="yellow")
        self.widget.tag_config("blue", foreground="blue")
        self.widget.tag_config("orange", foreground="orange")
        self.widget.tag_config("pink", foreground="pink")
        self.widget.tag_config("cyan", foreground="cyan")
        self.widget.tag_config("magenta", foreground="magenta")
        #self.widget.tag_config("fuchsia", foreground="fuchsia")

    def write(self, str_raw):
        # 获取锁
        echo_threadLock.acquire()
        # 背景是黑, 字体是白
        # self.tag = 'white'
        # self.widget.configure(state="normal")
        # self.widget.insert(END, str_raw, (self.tag,))
        # self.widget.configure(state="disabled")
        # self.widget.see(END)
        if self.type == "stdout" or self.type == "stderr":
            self.tag = 'white'
            self.widget.configure(state="normal")
            self.widget.insert(END, str_raw, (self.tag,))
            self.widget.configure(state="disabled")
            self.widget.see(END)
        # 背景是白, 字体是黑
        # elif self.type == 'stderr':
        #     self.tag = 'black'
        #     self.widget.configure(state="normal")
        #     self.widget.insert(END, str_raw, (self.tag,))
        #     self.widget.configure(state="disabled")
        #     self.widget.see(END)
        # flush
        self.widget.update()
        # 释放锁
        echo_threadLock.release()

    def Colored(self, str_raw, color='black', end='\n'):
        echo_threadLock.acquire()
        if end == '':
            str_raw = str_raw.strip('\n')
        self.tag = color
        self.widget.configure(state="normal")
        self.widget.insert(END, str_raw, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see(END)
        # flush
        self.widget.update()
        echo_threadLock.release()

    def flush(self):
       echo_threadLock.acquire()
       self.widget.update()
       echo_threadLock.release()

    def waitinh(self):
        echo_threadLock.acquire()
        self.widget.configure(state="normal")
        self.widget.insert(END, str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see(END)
        echo_threadLock.release()

class FrameProgress(tk.Frame):
    def __init__(self, parent, Prolength=200, maximum=200, **cnf):
        tk.Frame.__init__(self, master=parent, **cnf)
        bg = parent.cget("background")

        s = ttk.Style()
        #s.theme_use("clam")
        #颜色随偏好修改 部分设置只在特定主题有效果,否则为默认绿色
        s.configure(
            "fp.Horizontal.TProgressbar",
            troughcolor=bg,
            background="#0078d7",
            lightcolor="#0078d7",
            darkcolor="#0078d7",
            relief=tk.GROOVE
        )

        self.pBar = ttk.Progressbar(self, 
                                    length=Prolength, 
                                    orient="horizontal", 
                                    mode="determinate", 
                                    maximum=maximum,
                                    style="fp.Horizontal.TProgressbar")
        
        #sticky="wens" 上面length 值会被忽略
        self.pBar.pack(expand=0, fill=X)
        # self.pBar.grid(row=0, column=0, sticky="w")

        #父组件的大小不由子组件决定
        self.grid_propagate(False)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
    
from tkinter import Tk    
#复制字符到Windows剪切板
def addToClipboard(text):
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.update()
    r.destroy()

def seconds2hms(seconds):
    # 将秒数转换成时分秒
    # 返回类型为str类型
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)

#颜色输出函数
def color(str, color='black', end='\n'):
    #自动添加\n换行符号,方便自动换行
    sys.stdout.Colored(str+'\n', color, end)
        
def random_str(index):
    h = "abcdefghijklmnopqrstuvwxyz0123456789"
    salt_cookie = ""
    for i in range(index):
        salt_cookie += random.choice(h)
    return salt_cookie

def md5(text):
    # 创建一个md5对象
    md5 = hashlib.md5()
    
    # 使用update方法更新md5对象，传入需要加密的字符串
    # 注意：update方法需要传入字节类型的数据，因此需要先将字符串编码为字节
    md5.update(text.encode('utf-8'))
    
    # 使用hexdigest方法获取加密后的16进制字符串
    encrypted_text = md5.hexdigest()
    
    return encrypted_text

def Merge(dict1, dict2):
    res = {**dict1, **dict2} 
    return res

def byte_to_hex(pw):
    #pw = b'111111'
    temp = b''
    for x in pw:
        temp += binascii.a2b_hex('%02x' % int('{:08b}'.format(x)[::-1], 2))
    return temp

def open_html(fileURL):
    '''
    Save as HTML file and open in the browser
    '''
    hide = os.dup(1)
    os.close(1)
    os.open(os.devnull, os.O_RDWR)
    try:
        file = "file:///%s" % os.path.abspath(fileURL)
        if sys.platform == 'linux' or sys.platform == 'linux2':
            subprocess.call(["xdg-open", file])
        else:
            webbrowser.open(file)
    except Exception as e:
        print("Output can't be saved in %s \
            due to exception: %s" % (fileURL, e))
    finally:
        os.dup2(hide, 1)
#补足8位并返回bytes =================>如果是3DES，要import DES3,然后 add_to_16即可
def add_to_8(value):
    while len(value) % 8 != 0:
        value = value + "\0"
    return value.encode(encoding='utf-8')

# str不是16的倍数那就补足为16的倍数
def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes

# #加密方法
# def aes_enc(text,key):
#     from Crypto.Cipher import AES
#     # 初始化加密器
#     aes = AES.new(add_to_16(key), AES.MODE_ECB)
#     #先进行aes加密
#     encrypt_aes = aes.encrypt(add_to_16(text))
#     #用base64转成字符串形式
#     encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
#     return encrypted_text

# #解密方法
# def aes_dec(text,key):
#     # 初始化加密器
#     from Crypto.Cipher import AES
#     aes = AES.new(add_to_16(key), AES.MODE_ECB)
#     #优先逆向解密base64成bytes
#     base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
#     #
#     decrypted_text = str(aes.decrypt(base64_decrypted),encoding='utf-8') # 执行解密密并转码返回str
#     decrypted_text=decrypted_text.rstrip('\0')
#     return decrypted_text

#DES加密(还有点问题)
# def des_enc(text,ENCRYPT_KEY):
#     text = request.quote(text)
#     aes = DES.new(add_to_8(ENCRYPT_KEY),DES.MODE_ECB)
#
#     encrypt_aec = aes.encrypt(add_to_8(text))
#     encrypt_text = str(base64.encodebytes(encrypt_aec),encoding="utf-8").strip()
#     return encrypt_text

#DES解密
# def des_dec(text,ENCRYPT_KEY):
#     aes = DES.new(add_to_8(ENCRYPT_KEY),DES.MODE_ECB)
#     decrypt_aec = base64.decodebytes(text.encode(encoding='utf-8'))
#     decrypt_text = aes.decrypt(decrypt_aec)
#     #去除末尾的\x07
#     decrypt_text = str(decrypt_text[:-decrypt_text[-1]],encoding='utf-8')
#     decrypt_text = request.unquote(decrypt_text)
#     return decrypt_text


def get_sha1(string):
    from hashlib import sha1
    s1=sha1()
    s1.update(string.encode('utf8'))
    return s1.hexdigest()

def get_middle_text(text, prefix, suffix, index=0):
    """
    Simple implementation of obtaining intermediate text
    :param text:Full text to get
    :param prefix:To get the first part of the text
    :param suffix: To get the second half of the text
    :param index: Where to get it from
    :return:
    """
    try:
        index_1 = text.index(prefix, index)
        index_2 = text.index(suffix, index_1 + len(prefix))
    except ValueError:
        # logger.log(CUSTOM_LOGGING.ERROR, "text not found pro:{} suffix:{}".format(prefix, suffix))
        return ''
    return text[index_1 + len(prefix):index_2]

#打开脚本目录
def LoadCMD(folder_name):
    from lib.settings import rootPath
    start_directory = rootPath + folder_name
    os.startfile(start_directory) 

def set_theme(theme):
    try:
        # 创建与数据库的连接，并使用with语句确保正确关闭连接
        with sqlite3.connect('./lib/db/database.db') as conn:
            # 创建游标对象
            cursor = conn.cursor()
            # 执行参数化查询
            cursor.execute("UPDATE config SET value = ? WHERE name = ?", (theme, "theme"))
            conn.commit()
    except sqlite3.Error as e:
        print(e)

def get_theme():
    try:
        # 创建与数据库的连接，并使用with语句确保正确关闭连接
        with sqlite3.connect('./lib/db/database.db') as conn:
            # 创建游标对象
            cursor = conn.cursor()
            # 执行参数化查询
            cursor.execute("SELECT value FROM config WHERE name = ?", ("theme",))
            result = cursor.fetchone()
            if result:
                theme = result[0]
                return theme
            else:
                return None
    except sqlite3.Error as e:
        print(e)

def opendir(path):
    os.startfile(path)

def baseurl(url):
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc
    return base_url

def read_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        long_text = file.read()
    return long_text

#删除text组件的内容
def delText(text):
    text.configure(state="normal")
    text.delete('1.0','end')
    text.configure(state="disabled")

def thread_it(func, **kwargs):
    t = threading.Thread(target=func, kwargs=kwargs)
    t.setDaemon(True)
    # 启动
    t.start()