# -*- coding:UTF-8 -*-
from lib.settings import variable_dict
from tkinter import Toplevel,Frame,Checkbutton,Label,ttk,Entry,Button
from tkinter import W
import socket
import socks
import os

class TopProxy():
    def __init__(self, gui):
        global variable_dict
        self.proxy = Toplevel(gui.root)
        self.proxy.withdraw()
        self.proxy.title("代理服务器设置")
        self.proxy.geometry('350x300+650+150')
        self.proxy.iconbitmap('python.ico')
        # 不允许扩大
        self.exchange = self.proxy.resizable(width=False, height=False)

        self.frmA = Frame(self.proxy, width=350, height=30, bg="whitesmoke")
        self.frmB = Frame(self.proxy, width=350, height=150, bg="whitesmoke")
        self.frmC = Frame(self.proxy, width=350, height=90, bg="whitesmoke")
        self.frmA.grid(row=0, column=0, padx=10, pady=10)
        self.frmB.grid(row=1, column=0, padx=2, pady=2)
        self.frmC.grid(row=2, column=0, padx=2, pady=2)

        self.frmA.grid_propagate(0)
        self.frmB.grid_propagate(0)
        self.frmC.grid_propagate(0)

        self.button1 = Checkbutton(self.frmA,text="启用",command=lambda:self.Yes(),variable=variable_dict["Proxy_CheckVar1"])
        self.button2 = Checkbutton(self.frmA,text="禁用",command=lambda:self.No(),variable=variable_dict["Proxy_CheckVar2"])
        
        self.button1.grid(row=0, column=0)
        self.button2.grid(row=0, column=1)

        self.LabA = Label(self.frmB, text='类   型')
        
        self.cobA = ttk.Combobox(self.frmB,width=12,textvariable=variable_dict["PROXY_TYPE"],state='readonly')
        # 绑定参数
        self.cobA.bind("<<ComboboxSelected>>", self.bind_combobox_3)
        self.cobA["values"]=("HTTP/HTTPS","SOCKS5","SOCKS4")

        self.LabB = Label(self.frmB, text='IP地址')
        self.EntB = Entry(self.frmB, width=25, textvariable=variable_dict["Proxy_addr"])

        self.LabC = Label(self.frmB, text='端   口')
        self.EntC = Entry(self.frmB, width=25, textvariable=variable_dict["Proxy_port"])

        self.LabD = Label(self.frmB, text='账   号')
        self.EntD = Entry(self.frmB, width=25, textvariable=variable_dict["Proxy_user"]) 

        self.LabE = Label(self.frmB, text='密   码')
        self.EntE = Entry(self.frmB, width=25, textvariable=variable_dict["Proxy_pwd"])

        self.LabA.grid(row=0, column=0, padx=2, pady=2, sticky=W)
        self.cobA.grid(row=0, column=1, padx=2, pady=2, sticky=W)

        self.LabB.grid(row=1, column=0, padx=2, pady=2, sticky=W)
        self.EntB.grid(row=1, column=1, padx=2, pady=2, sticky=W)

        self.LabC.grid(row=2, column=0, padx=2, pady=2, sticky=W)
        self.EntC.grid(row=2, column=1, padx=2, pady=2, sticky=W)
        
        self.LabD.grid(row=3, column=0, padx=2, pady=2, sticky=W)
        self.EntD.grid(row=3, column=1, padx=2, pady=2, sticky=W)
        
        self.LabE.grid(row=4, column=0, padx=2, pady=2, sticky=W)
        self.EntE.grid(row=4, column=1, padx=2, pady=2, sticky=W)

        self.buttonD = Button(self.frmC,text='还原',width=20,command=self.old)
        self.buttonE = Button(self.frmC,text='输出代理',width=20,command=self.show_proxy)
        self.buttonD.grid(row=0,column=0,padx=2,pady=2)
        self.buttonE.grid(row=1,column=0,padx=2,pady=2)
        #关联回调函数
        self.proxy.protocol("WM_DELETE_WINDOW", self.close)

    def hide(self):
        """
        隐藏界面
        """
        self.proxy.withdraw()
        
    def show(self):
        """
        显示界面
        """
        self.proxy.update()
        self.proxy.deiconify()
        
    def close(self):
        """
        关闭界面
        """
        self.hide()
        
    def Yes(self):
        variable_dict["Proxy_CheckVar2"].set(0)
        if variable_dict["Proxy_CheckVar1"].get() == 1:
            proxy_str = variable_dict["PROXY_TYPE"].get()
            ip = self.EntB.get() if self.EntB.get() else None
            port = self.EntC.get() if self.EntC.get() else None
            user = self.EntD.get() if self.EntD.get() else None
            pwd = self.EntE.get() if self.EntE.get() else None

            if proxy_str == "HTTP/HTTPS":
                os.environ['HTTP_PROXY'] = ip+':'+port
                os.environ['HTTPS_PROXY'] = ip+':'+port
            else:
                if proxy_str == "SOCKS4":
                    proxy_type = socks.SOCKS4
                elif proxy_str == "SOCKS5":
                    proxy_type = socks.SOCKS5
                socks.set_default_proxy(proxy_type, ip, int(port), username=user, password=pwd)
                socket.socket = socks.socksocket
            print('[*]设置代理成功')
        else:
            socks.set_default_proxy(None)
            socket.socket = socks.socksocket
            os.environ['HTTP_PROXY'] = ''
            os.environ['HTTPS_PROXY'] = ''
            print('[*]取消代理')

    def No(self):
        variable_dict["Proxy_CheckVar1"].set(0)
        if variable_dict["Proxy_CheckVar2"].get() == 1:
            socks.set_default_proxy(None)
            socket.socket = socks.socksocket
            os.environ['HTTP_PROXY'] = ''
            os.environ['HTTPS_PROXY'] = ''
            print('[*]禁用代理')
            
    def old(self):
        variable_dict["Proxy_CheckVar1"].set(0)
        variable_dict["Proxy_CheckVar2"].set(0)
        variable_dict["PROXY_TYPE"].set('HTTP/HTTPS')
        variable_dict["Proxy_addr"].set('127.0.0.1')
        variable_dict["Proxy_port"].set('8080')
        variable_dict["Proxy_user"].set('')
        variable_dict["Proxy_pwd"].set('')
        socks.set_default_proxy(None)
        socket.socket = socks.socksocket
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''
        
    def show_proxy(self):
        print('[*]HTTP_PROXY: '+os.environ['HTTP_PROXY'])
        print('[*]HTTPS_PROXY: '+os.environ['HTTPS_PROXY'])
        
    def bind_combobox_3(self, *args):
        x = variable_dict["PROXY_TYPE"].get()
        if x == 'SOCKS5' or x == 'SOCKS4':
            variable_dict["Proxy_port"].set('1080')
        else:
            variable_dict["Proxy_port"].set('8080')