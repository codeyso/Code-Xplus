# -*- coding:UTF-8 -*-
from tkinter import messagebox, Toplevel, Menu, Frame
from tkinter import BOTH, INSERT, END
from keyword import kwlist
from lib.core.widgets.MyTextEditor import TextEditor
import importlib
import os

# 内置函数
bifs = dir(__builtins__)
# 关键字
kws = kwlist

# 编辑代码界面类
class CodeFile():
    # 添加类变量用于跟踪打开的窗口
    _opened_windows = {}

    def __init__(self, root, file_name, Logo, vuln_select, text=''):
        # 检查文件是否已打开
        if file_name in CodeFile._opened_windows:
            existing_window = CodeFile._opened_windows[file_name]
            if existing_window.file.winfo_exists():
                # 如果窗口存在，将其提升到顶层
                existing_window.file.lift()
                existing_window.file.focus_force()
                return
            else:
                # 如果窗口已不存在，从字典中移除
                del CodeFile._opened_windows[file_name]

        if Logo == '2':
            self.file_name1 = './exp/' + file_name + '.py'
        elif Logo == '3':
            self.file_name1 = './lib/tamper/' + file_name + '.py'
        else:
            self.file_name1 = './poc/' + file_name + '.py'
        if os.path.exists(self.file_name1) == False:
            messagebox.showinfo(title='提示', message='还未选择模块')
            return
        # 创建窗口和其他组件
        self.vuln_select = vuln_select
        self.file_name = file_name
        self.file = Toplevel(root)
        self.file.title("文本编辑")
        # self.file.geometry('1000x600+450+150')
        self.file.iconbitmap('python.ico')
        # 计算并设置窗口居中
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - (1000 // 2)
        y = (screen_height // 2) - (600 // 2)
        # 使用 place 方法手动设置位置
        self.file.geometry(f'1000x600+{x}+{y}')
        # 确保更新
        self.file.update_idletasks()
        # 定位字符
        self.text = 'def ' + text
        #
        self.colorobj = self._codefilter = None
        # 顶级菜单
        self.menubar = Menu(self.file)
        self.menubar.add_command(label="保 存", accelerator="ctrl + s",
                                 command=lambda: self.save_file('1', self.vuln_select))
        self.menubar.add_command(label="撤 销", accelerator="Ctrl + Z", command=self.move)
        self.menubar.add_command(label="Dnslog", command=self.switch_Dnslog)
        self.menubar.add_command(label="Ceye", command=self.switch_Ceye)

        self.file.bind("<Control-s>", lambda event: self.save_file('1', self.vuln_select))
        # 绑定关闭事件
        # 将新窗口实例保存到类变量中
        CodeFile._opened_windows[file_name] = self

        # 修改关闭事件处理
        def _on_close():
            if self.file_name in CodeFile._opened_windows:
                del CodeFile._opened_windows[self.file_name]
            self.file.destroy()

        self.file.protocol("WM_DELETE_WINDOW", _on_close)
        # 显示菜单
        self.file.config(menu=self.menubar)

        self.frmA = Frame(self.file, width=1000, height=600, bg="white")
        self.frmA.pack(fill=BOTH, expand=1)

        self.TexA = TextEditor(self.frmA)
        self.TexA.pack(fill=BOTH, expand=1)
        self.TexA.text_area.tag_config('bif', foreground='orange')
        self.TexA.text_area.tag_config('kw', foreground='purple')
        self.TexA.text_area.tag_config('comment', foreground='red')
        self.TexA.text_area.tag_config('string', foreground='green')

        self.openRender()

    def switch_Dnslog(self):
        Loadfile_text = self.TexA.text_area.get('0.0', 'end').strip('\n')
        self.TexA.text_area.delete('1.0', 'end')
        Loadfile_text = Loadfile_text.replace('Ceye', 'Dnslog')
        self.TexA.text_area.insert(INSERT, Loadfile_text)

    def switch_Ceye(self):
        Loadfile_text = self.TexA.text_area.get('0.0', 'end').strip('\n')
        self.TexA.text_area.delete('1.0', 'end')
        Loadfile_text = Loadfile_text.replace('Dnslog', 'Ceye')
        self.TexA.text_area.insert(INSERT, Loadfile_text)

    def on_close(self):
        # 在这里可以添加任何清理代码
        self.file.destroy()  # 关闭窗口

    def move(self):
        self.TexA.text_area.edit_undo()

    def openRender(self):
        try:
            with open(self.file_name1, mode='r', encoding='utf-8') as f:
                array = f.readlines()
                for i in array:  # 遍历array中的每个元素
                    self.TexA.text_area.insert(INSERT, i)
            if self.text and self.text != 'ALL' and self.text != 'def ':
                idx = '1.0'
                idx = self.TexA.text_area.search(self.text, idx, nocase=1, stopindex=END)
                if idx:
                    # 跳转到指定行
                    self.TexA.text_area.see(idx)
                    lineinfo = self.TexA.text_area.dlineinfo(idx)
                    self.TexA.text_area.yview_scroll(lineinfo[1], 'pixels')
                    # self.TexA.text_area.mark_set('insert', idx.split('.')[0]+'.0')
        except FileNotFoundError:
            print('[-]还未选择模块,无法编辑')
        except Exception as e:
            messagebox.showerror(title='结果', message=e)

    def save_file(self, event, vuln_select):
        try:
            save_data = str(self.TexA.text_area.get('0.0', 'end'))
            fobj_w = open(self.file_name1, 'w', encoding='utf-8')
            fobj_w.writelines(save_data.strip('\n'))
            fobj_w.close()
            if vuln_select is not None:
                vuln_select = importlib.reload(vuln_select)
            print('[*]保存成功, %s 模块已重新载入!' % self.file_name)
        except Exception as e:
            print("异常对象的内容是%s" % e)
            messagebox.showerror(title='结果', message='出现错误')