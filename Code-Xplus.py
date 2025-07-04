# -*- coding:UTF-8 -*-
from tkinter import ttk, messagebox, scrolledtext, Toplevel, Tk, Menu, Frame, Button, Label, Entry, Text, Spinbox, \
    Checkbutton, IntVar, simpledialog
from tkinter import BOTH, INSERT, END, W, TOP, BOTTOM, X, LEFT, NONE, RIGHT, Y
from PIL import Image, ImageTk
import tkinter as tk

from lib.clasetting import TextRedirector, color, FrameProgress, seconds2hms, LoadCMD, delText, set_theme, get_theme
import lib.util.globalvar as GlobalVar

from concurrent.futures import ThreadPoolExecutor
from openpyxl import Workbook

import prettytable as pt
import os, sys, time
import importlib, glob, re
import threading, math
import urllib3
import inspect
import ctypes

# 支持TLSv1.0和TLSv1.1
os.environ['COMPOSE_TLS_VERSION'] = "TLSv1_2"
# 去除错误警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# 调用api设置成由应用程序缩放
if sys.platform == "win32":
    try:
        # version >= win 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass

# 调用api获得当前的缩放因子
try:
    # version >= win 8
    scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
except:
    # version win 7 or less
    scaleFactor = 125

# 主界面类
class MyGUI:
    # POC界面当前加载的对象
    vuln = None
    # 填充线程列表,创建多个存储POC脚本的界面, 默认为1, 2, 3, 4
    threadList = []
    # 线程锁
    threadLock = threading.Lock()
    # poc下的脚本文件列表
    scripts = []
    # poc首字母
    uppers = []
    # 用于wait_running函数
    wait_index = 0
    # 选中的checkbutton,代表执行的POC脚本名称
    Checkbutton_text = ''
    # 保存多个checkbutton关联的变量
    var = {}
    # 用于生成checkbutton处的定位
    row = 1
    # 当前脚本名称
    vul_name = ''
    # 当前结果文件
    wb = None
    # excel表格
    ws = None
    # 批量结果保存开关
    wbswitch = ''
    # 屏幕存储
    screens = []
    # 对象属性参数字典
    frms = []
    current_match_index = -1  # 当前匹配项索引
    matches = []  # 存储匹配项位置
    # 初始化窗体对象
    def __init__(self):
        self.root = Tk()
        self.root.tk.call('tk', 'scaling', scaleFactor / 75)
        self.root.iconbitmap('python.ico')
        # 设置title
        self.title = self.root.title('Code-Xplus')
        # 设置窗体大小，1160x750是窗体大小，400+50是初始位置
        self.size = self.root.geometry('1200x800+400+50')
        # 创建样式
        self.style = ttk.Style()
        self.available_themes = self.style.theme_names()
        # 当前选中的主题
        self.current_theme = get_theme()
        # 创建一个字典来存储每个主题的勾选状态
        self.theme_vars = {theme: tk.IntVar() for theme in self.available_themes}
        # 不允许扩大
        # self.exchange = self.root.resizable(width=False, height=False)
        self.root.columnconfigure(0, weight=1)
        # 对象属性参数字典
        self.frms = self.__dict__
        # 创建顶级菜单
        self.menubar = Menu(self.root)
        # 创建一个菜单
        self.menubar_1 = Menu(self.root, tearoff=False)
        # 创建一个菜单
        self.menubar_2 = Menu(self.root, tearoff=False)
        # 创建一个菜单
        self.menubar_3 = Menu(self.root, tearoff=False)

        # 顶级菜单添加一个子菜单
        self.menubar1 = Menu(self.root, tearoff=False)
        self.menubar1.add_command(label="根目录", command=lambda: LoadCMD('/'))
        self.menubar.add_cascade(label="打开文件", menu=self.menubar1)
        # 顶级菜单增加一个普通的命令菜单项
        self.menubar.add_command(label="设置代理", command=lambda: myproxy.show())
        # 添加主题菜单
        self.menubar3 = Menu(self.root, tearoff=False)
        # 添加主题选项
        for theme in self.available_themes:
            self.menubar3.add_checkbutton(
                label=theme,
                variable=self.theme_vars[theme],
                command=lambda t=theme: self.switch_theme(t))
        self.menubar.add_cascade(label="UI配置", menu=self.menubar3)
        # 显示菜单
        self.root.config(menu=self.menubar)

    def CreateFrm(self):
        self.frmTOP = Frame(self.root, width=1160, height=35, bg='whitesmoke')
        self.frmPOC = Frame(self.root, width=1160, height=700, bg='whitesmoke')

        # 界面列表
        MyGUI.screens.append(self.frmPOC)

        # 界面初始化
        self.frmTOP.pack(side=TOP, expand=0, fill=X)
        self.frmPOC.pack(side=BOTTOM, expand=1, fill=BOTH)

        # 创建按钮
        # Create a PhotoImage object from the icon file
        self.frmTOPimg1 = Image.open('./icons/信息收集.png')
        self.frmTOPphoto1 = ImageTk.PhotoImage(self.frmTOPimg1)
        self.frmTOPButton1 = Button(self.frmTOP, text='信息收集', command=lambda: switchscreen(self.frmPOC),
                                    image=self.frmTOPphoto1, compound="left")

        # 一、pack布局
        # side=LEFT（靠左对齐）
        # expand=1（允许扩大）
        # fill=BOTH（窗体占满整个窗口剩余的空间）
        # 信息收集
        self.frmTOPButton1.pack(side=LEFT, expand=0, fill=BOTH)

        # 定义frame
        # 此处 height 可控制按钮高度
        self.frmPOC_A = Frame(self.frmPOC, width=860, height=680, bg='whitesmoke')
        self.frmPOC_B = Frame(self.frmPOC, width=300, height=680, bg='whitesmoke')
        # pack定位
        self.frmPOC_A.pack(side=LEFT, expand=1, fill=BOTH)
        self.frmPOC_B.pack(side=RIGHT, expand=0, fill=Y)

        self.frmA = Frame(self.frmPOC_A, width=860, height=20, bg='white')
        self.frmB = Frame(self.frmPOC_A, width=860, height=580, bg='whitesmoke')
        self.frmC = Frame(self.frmPOC_A, width=860, height=40, bg='whitesmoke')
        self.frmE = Frame(self.frmPOC_B, width=300, height=40, bg='white')
        self.frmD = Frame(self.frmPOC_B, width=300, height=580, bg='whitesmoke')
        self.frmF = Frame(self.frmPOC_B, width=300, height=40, bg='white')

        self.frmA.pack(side=TOP, expand=0, fill=X)
        self.frmB.pack(side=TOP, expand=1, fill=BOTH)
        self.frmC.pack(side=TOP, expand=0, fill=X)

        # expand=0, fill=X 窗体不允许扩大,在X轴方向上填充
        self.frmE.pack(side=TOP, expand=0, fill=X)
        self.frmD.pack(side=TOP, expand=1, fill=BOTH)
        self.frmF.pack(side=TOP, expand=0, fill=X)

    # 创造第一象限
    def CreateFirst(self):
        # 目标框
        self.LabA = Label(self.frmA, text='目标')
        self.EntA = Entry(self.frmA, width='55', highlightcolor='red', highlightthickness=1, font=("consolas", 10))
        self.EntA.bind('<Key-Return>', lambda v=0: self.thread_it(self.verify, **{'url': self.EntA.get(),
                                                                                  'pool_num': int(
                                                                                      Ent_A_Top_thread.get())}))
        # 运行状态框
        self.LabA2 = Label(self.frmA, text='运行状态')
        self.TexA2 = Text(self.frmA, font=("consolas", 10), width=2, height=1)
        # 批量导入文件
        # Create a PhotoImage object from the icon file
        self.imgA = Image.open('./icons/多重输入.png')
        self.photoA = ImageTk.PhotoImage(self.imgA)
        self.ButtonA = Button(self.frmA, text='', command=lambda: myurls.show(), image=self.photoA, compound="left")
        # 线程池数量
        self.LabA3 = Label(self.frmA, text='线程(默认10)')
        self.b1 = Spinbox(self.frmA, from_=1, to=10, wrap=True, width=3, font=("consolas", 10),
                          textvariable=Ent_A_Top_thread)

        # pack布局
        self.LabA.pack(side=LEFT, expand=0, fill=NONE)
        self.EntA.pack(side=LEFT, expand=1, fill=X)
        self.LabA2.pack(side=LEFT, expand=0, fill=NONE)
        self.TexA2.pack(side=LEFT, expand=0, fill=NONE)
        self.ButtonA.pack(side=LEFT, expand=0, fill=BOTH)
        self.LabA3.pack(side=LEFT, expand=0, fill=NONE)
        self.b1.pack(side=LEFT, expand=0, fill=NONE)

        # 锁定屏幕,不允许写入
        self.TexA2.configure(state="disabled")

    # 创造第二象限
    def CreateSecond(self):
        self.TexB = scrolledtext.ScrolledText(self.frmB, font=("consolas", 9), width=105, bg='black')
        # 提前定义颜色
        self.TexB.tag_add("here", "1.0", "end")
        self.TexB.tag_config("here", background="black")
        # 设置插入光标的颜色
        self.TexB.config(insertbackground='white')
        self.TexB.pack(side=TOP, expand=1, fill=BOTH)
        # 绑定右键鼠标事件
        self.TexB.bind('<Control-f>', self.find_text)  # 该语句是在_create_body_函数内部
        self.TexB.bind('<Control-F>', self.find_text)  # 该语句是在_create_body_函数内部
        self.frame_progress = FrameProgress(self.frmB, height=10, maximum=1000)
        self.frame_progress.pack(side=BOTTOM, expand=0, fill=X)

    # 创造第三象限
    def CreateThird(self):
        self.ButtonC1 = Button(self.frmC, text='验 证', width=10, command=lambda: self.thread_it(self.verify, **{
            'url': self.EntA.get(), 'pool_num': int(Ent_A_Top_thread.get())}))
        self.ButtonC2 = Button(self.frmC, text='终 止', width=10, command=lambda: self.thread_it(self.stop_thread))
        self.ButtonC3 = Button(self.frmC, text='清空信息', width=15, command=lambda: delText(gui.TexB))
        self.ButtonC4 = Button(self.frmC, text='重新载入当前POC', width=15, command=lambda: reLoad(MyGUI.vuln))
        self.ButtonC5 = Button(self.frmC, text='当前线程运行状态', width=15, command=ShowPython)
        self.ButtonC6 = Button(self.frmC, text='保存批量检测结果', width=15, command=save_result)

        # 表格布局
        self.ButtonC1.grid(row=0, column=0, padx=2, pady=2)
        self.ButtonC2.grid(row=0, column=1, padx=2, pady=2)
        self.ButtonC3.grid(row=0, column=2, padx=2, pady=2)
        self.ButtonC4.grid(row=0, column=3, padx=2, pady=2)
        self.ButtonC5.grid(row=0, column=4, padx=2, pady=2)
        self.ButtonC6.grid(row=0, column=5, padx=2, pady=2)

    # 创造第四象限
    def CreateFourth(self):
        self.ButtonE1 = Button(self.frmE, text='加载POC', width=8, command=lambda: self.loadPoc())
        self.ButtonE2 = Button(self.frmE, text='编辑文件', width=8,
                               command=lambda: CodeFile(gui.root, MyGUI.Checkbutton_text, '1', MyGUI.vuln, '', ))
        self.ButtonE3 = Button(self.frmE, text='打开脚本目录', width=10, command=lambda: LoadCMD('/poc'))
        self.ButtonE1.grid(row=0, column=0, padx=2, pady=2)
        self.ButtonE2.grid(row=0, column=1, padx=2, pady=2)
        self.ButtonE3.grid(row=0, column=2, padx=2, pady=2)

    def CreateFivth(self):
        # 创建Notebook组件
        self.note1 = ttk.Notebook(self.frmD, width=300, height=580, style='my.TNotebook')
        self.ButtonF1 = Button(self.frmF, text='<-', width=15, command=lambda: self.switch_frm('<-'))
        self.ButtonF2 = Button(self.frmF, text='->', width=15, command=lambda: self.switch_frm('->'))
        self.ButtonF1.pack(side=LEFT, expand=1, fill=BOTH)
        self.ButtonF2.pack(side=RIGHT, expand=1, fill=BOTH)

    def switch_theme(self, theme):
        # 更新当前主题
        # 取消之前的勾选
        self.theme_vars[self.current_theme].set(0)
        self.style.theme_use(theme)
        self.current_theme = theme
        # 勾选当前主题
        self.theme_vars[theme].set(1)
        set_theme(theme)

    def rightKey(self, event, menubar):
        menubar.delete(0, END)
        menubar.add_command(label='搜索', command=lambda: self.search_tool())
        menubar.add_command(label='刷新', command=lambda: self.delete_tool())
        menubar.add_command(label='新建文件', command=lambda: self.create_new_file())
        menubar.add_command(label='删除文件', command=lambda: self.delete_file())
        menubar.add_command(label='打开CMD', command=lambda: self.opencmd())
        menubar.post(event.x_root, event.y_root)

    def search_result(self, key, ignore_case, search_toplevel, search_box):
        # 移除之前的高亮标记
        self.TexB.tag_remove('match', '1.0', "end")
        self.TexB.tag_remove('next', '1.0', "end")
        MyGUI.matches.clear()  # 清空匹配项
        matches_found = 0

        if not key.strip():  # 检查输入是否为空或仅空格
            # messagebox.showinfo("提示", "查找内容不能为空！", parent=search_toplevel)
            return

        start_pos = '1.0'
        found = False  # 是否找到至少一个匹配项
        while True:
            start_pos = self.TexB.search(
                key,
                start_pos,
                nocase=ignore_case,
                stopindex=tk.END
            )
            if not start_pos:
                break
            found = True
            end_pos = f"{start_pos}+{len(key)}c"
            self.TexB.tag_add('match', start_pos, end_pos)
            MyGUI.matches.append(start_pos)  # 保存匹配项位置
            matches_found += 1
            start_pos = end_pos  # 继续查找下一个匹配

        # 配置高亮样式
        self.TexB.tag_config('match', background='#4169E1', foreground='white')
        self.TexB.tag_config('next', background='#00FF00', foreground='black')

        # 更新窗口标题和反馈
        if not found:
            # messagebox.showinfo("提示", "未找到匹配内容", parent=search_toplevel)
            search_toplevel.title("未找到匹配内容")
        else:
            self.current_match_index = 0  # 重置当前匹配索引
            search_toplevel.title(f"找到 {matches_found} 个匹配项")

        search_box.focus_set()  # 保持输入框焦点

    def find_next(self):
        if not MyGUI.matches:
            return
        self.current_match_index = (self.current_match_index + 1) % len(MyGUI.matches)
        self.highlight_current_match()

    def find_previous(self):
        if not MyGUI.matches:
            return
        self.current_match_index = (self.current_match_index - 1) % len(MyGUI.matches)
        self.highlight_current_match()

    def highlight_current_match(self):
        # 移除之前的高亮
        self.TexB.tag_remove('match', '1.0', "end")
        self.TexB.tag_remove('next', '1.0', "end")

        if MyGUI.matches:
            current_match = MyGUI.matches[self.current_match_index]
            end_pos = f"{current_match}+{len(self.search_toplevel.search_entry.get())}c"

            # 高亮当前匹配项为绿底黑色
            self.TexB.tag_add('next', current_match, end_pos)
            self.TexB.see(current_match)  # 滚动到当前匹配项

            # 将其他匹配项高亮为蓝底白色
            for i, match in enumerate(MyGUI.matches):
                if i != self.current_match_index:
                    self.TexB.tag_add('match', match, f"{match}+{len(self.search_toplevel.search_entry.get())}c")

    def find_text(self, event=None):
        # 窗口复用逻辑：如果窗口已存在则置顶
        if hasattr(self, 'search_toplevel') and self.search_toplevel.winfo_exists():
            self.search_toplevel.lift()
            self.search_toplevel.search_entry.select_range(0, tk.END)  # 选中原有文本方便修改
            return "break"

        # 创建新窗口
        self.search_toplevel = Toplevel(self.root)
        self.search_toplevel.title("查找文本")
        self.search_toplevel.transient(self.root)
        self.search_toplevel.geometry('400x150+700+500')
        self.search_toplevel.resizable(False, False)

        # 输入框布局
        Label(self.search_toplevel, text="查找内容:").grid(
            row=0, column=0, padx=5, pady=5, sticky='e'
        )

        self.search_entry = Entry(self.search_toplevel, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.search_entry.focus_set()
        self.search_toplevel.search_entry = self.search_entry  # 保存为窗口属性方便后续操作

        # 复选框布局
        self.ignore_case_var = IntVar()
        Checkbutton(
            self.search_toplevel,
            text="忽略大小写 (Aa)",
            variable=self.ignore_case_var
        ).grid(row=1, column=1, padx=5, pady=2, sticky='w')

        # 绑定事件处理函数
        self.search_entry.bind('<KeyRelease>', self.on_search_entry_change)

        # 查找前一个按钮
        prev_btn = Button(
            self.search_toplevel,
            text="查找前一个",
            command=self.find_previous,
            width=10
        )
        prev_btn.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

        # 查找下一个按钮
        next_btn = Button(
            self.search_toplevel,
            text="查找下一个",
            command=self.find_next,
            width=10
        )
        next_btn.grid(row=1, column=2, padx=5, pady=5, sticky='ew')

        # 查找按钮
        search_btn = Button(
            self.search_toplevel,
            text="全部选择",
            command=lambda: self.search_result(
                self.search_entry.get(),
                self.ignore_case_var.get(),
                self.search_toplevel,
                self.search_entry
            ),
            width=8
        )
        search_btn.grid(row=2, column=2, padx=5, pady=5, sticky='ew')

        # 回车键绑定
        self.search_entry.bind('<Return>', lambda e: search_btn.invoke())

        # 窗口关闭处理
        def on_close():
            MyGUI.matches.clear()  # 清空匹配项
            # 移除之前的高亮
            # self.TexB.tag_remove('match', '1.0', "end")
            # self.TexB.tag_remove('next', '1.0', "end")
            self.search_toplevel.destroy()
            del self.search_toplevel  # 清除实例属性

        self.search_toplevel.protocol('WM_DELETE_WINDOW', on_close)

        # 窗口布局调整：使输入框自适应缩放
        self.search_toplevel.columnconfigure(1, weight=1)
        return "break"

    def on_search_entry_change(self, event):
        # 获取输入框中的文本
        search_text = self.search_toplevel.search_entry.get()
        # 调用搜索结果方法
        self.search_result(search_text, self.ignore_case_var.get(), self.search_toplevel, self.search_toplevel.search_entry)

    def delete_tool(self):
        self.loadPoc()

    def create_new_file(self):
        """创建新的POC文件"""
        filename = simpledialog.askstring("新建文件", "请输入文件名(不需要.py后缀):")
        if filename:
            # 确保文件名不为空且合法
            filename = filename.strip()
            if not filename:
                messagebox.showerror("错误", "文件名不能为空")
                return
                
            # 构建完整的文件路径
            file_path = os.path.join('poc', f'{filename}.py')
            
            # 检查文件是否已存在
            if os.path.exists(file_path):
                messagebox.showerror("错误", f"文件 {filename}.py 已存在")
                return
            
            try:
                # 创建并写入文件
                poc_template = '''def check(**kwargs):\n    # 编写POC逻辑\n    # 示例代码\n    print("hello world")'''
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(poc_template)
                print(f'[+] 成功创建文件: {filename}.py')
                # 刷新POC列表并选中新文件
                self.loadPoc()
                # 设置新文件为当前选中
                MyGUI.Checkbutton_text = filename
                MyGUI.vuln = importlib.import_module('.%s' % filename, package='poc')
                MyGUI.var[filename].set(1)
                
                # 获取文件首字母并找到对应的标签页
                first_letter = filename[0].upper()
                for i in MyGUI.uppers:
                    if i == first_letter:
                        # 计算文件应该在哪个Frame中
                        index = 1
                        for script_name in MyGUI.scripts:
                            if script_name.upper().startswith(i):
                                if index > 18:
                                    break
                                index += 1
                        frame_name = f'frmD_{i}_{math.ceil(index/18)}'
                        # 切换到对应的标签页
                        if frame_name in self.frms:
                            self.note1.select(self.frms[frame_name])
                
                # 打开编辑界面
                # CodeFile(gui.root, filename, '1', MyGUI.vuln, '')
            except Exception as e:
                messagebox.showerror("错误", f"创建文件失败: {str(e)}")

    def delete_file(self):
        """删除POC文件"""
        if not MyGUI.Checkbutton_text or not MyGUI.vuln:
            messagebox.showinfo("提示", "请先选择要删除的文件")
            return
            
        # 弹出确认框
        if not messagebox.askyesno("确认删除", f"确定要删除文件 {MyGUI.Checkbutton_text}.py 吗？"):
            return
            
        try:
            file_path = os.path.join('poc', f'{MyGUI.Checkbutton_text}.py')
            os.remove(file_path)
            print(f'[+] 成功删除文件: {MyGUI.Checkbutton_text}.py')
            # 重置选中状态
            MyGUI.Checkbutton_text = ''
            MyGUI.vuln = None
            # 刷新POC列表
            self.loadPoc()
        except Exception as e:
            messagebox.showerror("错误", f"删除文件失败: {str(e)}")

    def search_tool(self):
        poc_name = simpledialog.askstring("搜索POC", "请输入POC关键字:")
        if poc_name:
            self.loadPoc(key=poc_name)

    def opencmd(self):
        path = rootPath + '/poc'
        path = path.replace('\\', '/')
        os.system(f'start cmd /k cd /d {path}')

    # 切换界面
    def switch_frm(self, str):
        ilist = []
        jdcit = {}
        index = self.note1.index('current')
        text = self.note1.tab(index)['text']
        tabs_list = self.note1.tabs()
        for i in tabs_list:
            if self.note1.tab(i)['text'] == text:
                # 下标
                ilist.append(self.note1.index(i))
                # self.note1.index(i)
                jdcit.update({self.note1.index(i): i})
        # 定位
        pos = ilist.index(index)
        if str == '<-':
            if pos == 0:
                return
            else:
                # 隐藏当前界面
                self.note1.hide(self.note1.index('current'))
                # 显示界面
                self.note1.add(jdcit[ilist[pos - 1]])
                # 选择指定的选项卡
                self.note1.select(jdcit[ilist[pos - 1]])
        elif str == '->':
            if pos == len(ilist) - 1:
                return
            else:
                # 隐藏当前界面
                self.note1.hide(self.note1.index('current'))
                # 显示界面
                self.note1.add(jdcit[ilist[pos + 1]])
                # 选择指定的选项卡
                self.note1.select(jdcit[ilist[pos + 1]])

    # 加载POC
    def loadPoc(self, key='all'):
        # 清空存储
        self.note1.destroy()
        MyGUI.uppers.clear()
        MyGUI.scripts.clear()
        MyGUI.var.clear()
        for frm in MyGUI.frms:
            self.frms[frm] = None
        MyGUI.frms.clear()
        style1 = ttk.Style()
        # 'se'再改nw,ne,sw,se,w,e,wn,ws,en,es,n,s试试
        style1.configure('my.TNotebook', tabposition='wn')
        # 创建Notebook组件
        self.note1 = ttk.Notebook(self.frmD, width=300, height=580, style='my.TNotebook')
        self.note1.pack(expand=1, fill=BOTH)
        try:
            for _ in glob.glob('poc/*.py'):
                script_name = os.path.basename(_).replace('.py', '')
                if script_name in ['__init__', 'GlobSettings']:
                    continue
                if key != 'all' and re.search(key, script_name, re.IGNORECASE) is None:
                    continue
                # 取脚本首字母
                i = script_name[0].upper()
                if i not in MyGUI.uppers:
                    MyGUI.uppers.append(i)
                MyGUI.scripts.append(script_name)
                m = IntVar()
                MyGUI.var.update({script_name: m})
            # 去重
            MyGUI.uppers = list(set(MyGUI.uppers))
            # 排序
            MyGUI.uppers.sort()
            self.CreateThread()
        except Exception as e:
            messagebox.showinfo('提示', '请勿重复加载')

    # 填充线程列表,创建多个存储POC脚本的界面
    def CreateThread(self):
        for i in MyGUI.uppers:
            index = 1
            for script_name in MyGUI.scripts:
                if script_name.upper().startswith(i):
                    if self.frms.get('frmD_' + i + '_' + str(math.ceil(index / 18)), None) is None:
                        MyGUI.frms.append('frmD_' + i + '_' + str(math.ceil(index / 18)))
                        # self.frmD width=300, height=580
                        self.frms['frmD_' + i + '_' + str(math.ceil(index / 18))] = Frame(self.frmD, width=290,
                                                                                          height=580, bg='whitesmoke')
                        # 绑定右键
                        self.frms['frmD_' + i + '_' + str(math.ceil(index / 18))].bind("<Button-3>",
                                                                                       lambda event: self.rightKey(
                                                                                           event, self.menubar_2))
                        # 装入框架到选项卡
                        self.note1.add(self.frms['frmD_' + i + '_' + str(math.ceil(index / 18))], text=i)
                    self.Create(self.frms['frmD_' + i + '_' + str(math.ceil(index / 18))], script_name, index)
                    index += 1
            # 只显示一个界面
            if index > 18:
                # 装入框架到选项卡
                self.note1.hide(self.frms['frmD_' + i + '_' + str(math.ceil(index / 18))])

    # 创建POC脚本选择Checkbutton
    def Create(self, frm, x, i):
        button = Checkbutton(frm, text=x, variable=MyGUI.var[x], command=lambda: self.callCheckbutton(x))
        button.grid(row=i, sticky=W)

    # 调用checkbutton按钮
    def callCheckbutton(self, x):
        if MyGUI.var[x].get() == 1:
            try:
                for key, value in MyGUI.var.items():
                    if key != x:
                        value.set(0)
                MyGUI.vuln = importlib.import_module('.%s' % x, package='poc')
                MyGUI.Checkbutton_text = x
                print('[*] %s 模块已准备就绪!' % x)
            except Exception as e:
                print('[*]异常对象的内容是:%s' % e)
        else:
            MyGUI.vuln = None
            print('[*] %s 模块已取消!' % x)

    # 多线程函数
    def thread_it(self, func, **kwargs):
        self.sub_thread = threading.Thread(target=func, name='子线程1', kwargs=kwargs)
        # 守护
        self.sub_thread.daemon = True
        # 启动
        self.sub_thread.start()

    # 停止线程
    def stop_thread(self):
        try:
            _async_raise(self.function_thread.ident, SystemExit)
            print("[*]已停止运行")
        except Exception as e:
            messagebox.showinfo('错误', str(e))
        finally:
            gui.TexA2.delete('1.0', 'end')
            gui.TexA2.configure(state="disabled")

    # 验证功能
    def verify(self, **kwargs):
        # 未选中模块
        if MyGUI.vuln == None:
            messagebox.showinfo(title='提示', message='还未选择模块')
            return
        MyGUI.vul_name = MyGUI.vuln.__name__.replace('poc.', '')
        myurlsTexA = GlobalVar.get_value("myurlsTexA")
        # 进度条初始化
        self.frame_progress.pBar["value"] = 0
        self.root.update()
        # 是否需要保存结果
        MyGUI.wbswitch = 'false'
        start = time.time()
        color('[*] {} 开始执行模块 {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), MyGUI.vul_name),
              'orange')
        # 进入单模块测试功能
        if kwargs['url']:
            try:
                # 执行状态
                self.status_thread = threading.Thread(target=wait_running, name='运行状态子线程', daemon=True)
                self.status_thread.start()
                # 运行函数
                self.function_thread = threading.Thread(target=MyGUI.vuln.check, kwargs=kwargs, name='执行函数子线程',
                                                        daemon=True)
                self.function_thread.start()
                self.function_thread.join()
            except Exception as e:
                print('出现错误: %s' % e)
            finally:
                _async_raise(self.status_thread.ident, SystemExit)
                gui.TexA2.delete('1.0', 'end')
                gui.TexA2.configure(state="disabled")
            end = time.time()
            print('[*]共花费时间：{} 秒'.format(seconds2hms(end - start)))
            
        # 进入多目标测试功能
        elif myurlsTexA.get('0.0', 'end').strip('\n'):
            # 去空处理
            file_list = [i for i in myurlsTexA.get('0.0', 'end').split("\n") if i != '']
            file_len = len(file_list)
            # 每执行一个任务增长的长度
            flag = round(1000 / file_len, 2)
            executor = ThreadPoolExecutor(max_workers=kwargs['pool_num'])
            # 存储目标列表
            url_list = []
            # 存储结果列表
            result_list = []
            for url in file_list:
                args = {'url': url}
                url_list.append(args)
            try:
                for data in executor.map(lambda kwargs: MyGUI.vuln.check(**kwargs), url_list):
                    # 如果结果是列表,去重一次
                    if type(data) == list:
                        data = list(set(data))
                    # 汇聚结果
                    result_list.append(data)
                    # 进度条
                    self.frame_progress.pBar["value"] += flag
                    self.root.update()
                # 根据结果生成表格
                index_list = [i + 1 for i in range(len(url_list))]
                # 合并列表
                print_result = zip(index_list, file_list, result_list)
                results_table = pt.PrettyTable()
                results_table.field_names = ["Index", "URL", "Result"]
                results_table.align['URL'] = 'l'
                results_table.align['Result'] = 'l'
                results_table.padding_width = 1
                # 保存结果
                MyGUI.wbswitch = 'true'
                # 构造初始环境
                # 当前结果文件
                MyGUI.wb = Workbook()
                # excel表格
                MyGUI.ws = MyGUI.wb.active
                MyGUI.ws.append(['Index', 'URL', 'Result'])
                index = 1
                # 输出结果
                for i in print_result:
                    MyGUI.ws.append(i)
                    results_table.add_row(i)
                    index += 1
                print(results_table)
                # 关闭线程池
                executor.shutdown()
            except Exception as e:
                print('执行脚本出现错误: %s ,建议在脚本加上异常处理!' % type(e))
                self.frame_progress.pBar["value"] = 1000
                self.root.update()
            finally:
                end = time.time()
                print('[*]共花费时间：{} 秒'.format(seconds2hms(end - start)))
        # 没有输入测试目标
        else:
            color('[*]请输入目标URL!', 'red')
            color('[*]请输入目标URL!', 'yellow')
            color('[*]请输入目标URL!', 'blue')
            color('[*]请输入目标URL!', 'green')
            color('[*]请输入目标URL!', 'orange')
            color('[*]请输入目标URL!', 'pink')
            color('[*]请输入目标URL!', 'cyan')

    # 开始循环
    def start(self):
        self.CreateFrm()
        self.CreateFirst()
        self.CreateSecond()
        self.CreateThird()
        self.CreateFourth()
        self.CreateFivth()

# 运行状态线程类
class Job(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True

    def run(self):
        while self.__running.isSet():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            wait_running()

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False

def thread_it(func, **kwargs):
    thread = threading.Thread(target=func, kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()

def stop_thread(thread):
    if thread is not None:
        try:
            _async_raise(thread.ident, SystemExit)
            # self.wait_running_job.stop()
            print("[*]已停止运行")
        except Exception as e:
            messagebox.showinfo('提示', e)

# 当前运行状态
def wait_running():
    MyGUI.wait_index = 0
    list = ["\\", "|", "/", "—"]
    gui.TexA2.configure(state="normal")
    while True:
        index = MyGUI.wait_index % 4
        gui.TexA2.insert(INSERT, list[index])
        time.sleep(0.5)
        gui.TexA2.delete('1.0', 'end')
        MyGUI.wait_index = MyGUI.wait_index + 1

# 终止子线程
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

# 返回分隔符号函数
def Separator_(str_):
    index = 104 - len(str_)
    left = math.ceil(index / 2)
    right = math.floor(index / 2)
    return '-' * left + str_ + '-' * right

# 显示线程运行状态
def ShowPython():
    try:
        print('[*]' + gui.sub_thread.getName() + ' 运行状态: ' + str(gui.sub_thread.isAlive()))
        print('[*]' + gui.status_thread.getName() + ' 运行状态: ' + str(gui.status_thread.isAlive()))
        print('[*]' + gui.function_thread.getName() + ' 运行状态: ' + str(gui.function_thread.isAlive()))
    except AttributeError:
        messagebox.showinfo(title='提示', message='进程还未启动')
    except Exception as e:
        messagebox.showinfo(title='错误', message=e)

def save_result():
    # if MyGUI.vul_name != '' and MyGUI.wbswitch == 'true':
    if MyGUI.wbswitch == 'true':
        timestr = time.strftime("%Y%m%d_%H%M%S")  # 获取当前时间
        print('[*]已保存检测结果 -> %s_%s.xlsx' % (MyGUI.vul_name, timestr))
        MyGUI.wb.save('./lib/result/%s_%s.xlsx' % (MyGUI.vul_name, timestr))
        # 不清空数据
        # MyGUI.wb = None
        # MyGUI.ws = None
    else:
        print('[-]未找到批量检测结果, 请先执行脚本测试!')

# 重载脚本函数
def reLoad(vuln):
    try:
        if vuln == None:
            messagebox.showerror(title='错误', message='未载入脚本!')
            return
        vuln = importlib.reload(vuln)
        print('[*]重新载入成功!')
    except Exception as e:
        messagebox.showinfo(title='重新载入失败', message=str(e))

def switchscreen(frame):
    for screen in MyGUI.screens:
        # grid布局 grid_remove()
        # pack布局 pack_forget()
        screen.pack_forget()

    frame.pack(side=BOTTOM, expand=1, fill=BOTH)
    if frame == gui.frmPOC:
        # 输出重定向到POC界面
        sys.stdout = TextRedirector(gui.TexB, "stdout")

# 取消未执行的任务
def CancelThread():
    thread_list = GlobalVar.get_value('thread_list')
    if len(thread_list) == 0:
        messagebox.showinfo(title='提示', message='没有正在运行的任务~')
        return
    index = 0
    for task in thread_list:
        try:
            if task.cancel() == True:
                index += 1
        except Exception as e:
            print(e)
            continue
    messagebox.showinfo(title='提示', message="[*]共有 %s 个任务\n[*]执行 %s 个任务\n[-]取消 %s 个任务" % (
    len(thread_list), str(len(thread_list) - index), str(index)))

# 退出时执行的函数
def callbackClose():
    if messagebox.askokcancel('提示', '要退出程序吗?') == True:
        # 当无异常发生,退出程序
        sys.exit(0)

if __name__ == "__main__":
    # 创建主界面
    gui = MyGUI()
    # 初始化全局变量
    GlobalVar._init()
    # 定义Treeview每个组件高度
    gui.style.configure('Treeview', rowheight=18)
    gui.style.configure('red.TSeparator', background='red')
    images = (
        tk.PhotoImage("img_close", data='''
                    R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                    d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                    5kEJADs=
                    '''),
        tk.PhotoImage("img_closeactive", data='''
                    R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                    AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                    '''),
        tk.PhotoImage("img_closepressed", data='''
                    R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                    d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                    5kEJADs=
                ''')
    )
    gui.style.element_create("close", "image", "img_close",
                         ("active", "pressed", "!disabled", "img_closepressed"),
                         ("active", "!disabled", "img_closeactive"), border=8, sticky='')
    gui.style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
    gui.style.layout("CustomNotebook.Tab", [
        ("CustomNotebook.tab", {
            "sticky": "nswe",
            "children": [
                ("CustomNotebook.padding", {
                    "side": "top",
                    "sticky": "nswe",
                    "children": [
                        ("CustomNotebook.focus", {
                            "side": "top",
                            "sticky": "nswe",
                            "children": [
                                ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                            ]
                        })
                    ]
                })
            ]
        })
    ])
    # 导入变量
    from lib.settings import rootPath, Ent_A_Top_thread, Ent_A_Top_Text
    # 初始化配置文件
    settings_vuln = importlib.import_module('.GlobSettings', package='poc')
    GlobalVar.set_value('settings_vuln', settings_vuln)
    GlobalVar.set_value('screens', MyGUI.screens)
    # 初始化全局代理变量
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''
    # 初始化漏洞扫描界面
    gui.start()
    GlobalVar.set_value('gui', gui)
    from lib.core import Loadfile, CodeFile, TopProxy
    # 输出重定向
    sys.stdout = TextRedirector(gui.TexB, "stdout")
    # 标准错误重定向
    sys.stderr = TextRedirector(gui.TexB, "stderr")
    # 多目标输入界面
    myurls = Loadfile(gui)
    GlobalVar.set_value('myurls', myurls)
    # 设置代理
    myproxy = TopProxy(gui)
    GlobalVar.set_value('myproxy', myproxy)
    # 1、当在应用程序启动时设置主题, tkinter 会根据该主题的设计加载所有控件的样式
    # 2、当在控件创建后设置主题, 控件可能不会立即更新为新主题的样式。tkinter 不会自动重新渲染已经创建的控件
    # 通过函数修改主题是在控件创建后, 为了确保显示一致性, 将初次设置主题的时间点放在控件创建后
    gui.switch_theme(get_theme())
    # INSERT表示输入光标所在的位置，初始化后的输入光标默认在左上角
    gui.TexB.insert(INSERT, Ent_A_Top_Text.lstrip('\n'), ('white',))
    gui.TexB.configure(state="disabled")
    # 自定义退出函数
    gui.root.protocol("WM_DELETE_WINDOW", callbackClose)
    gui.root.mainloop()
