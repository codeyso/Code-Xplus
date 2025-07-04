# -*- coding:UTF-8 -*-
import tkinter as tk
from tkinter import scrolledtext, Toplevel, Entry, Label, Button, Checkbutton
from tkinter import INSERT, IntVar
from idlelib.colorizer import ColorDelegator
from idlelib.percolator import Percolator

class TextEditor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)

        # 创建行号文本框
        self.line_number = tk.Text(self, width=4, padx=3, takefocus=0, border=0,
                                   background='#f0f0f0', state='disabled', font=("consolas", 10))
        self.line_number.pack(side=tk.LEFT, fill=tk.Y)

        # 创建可滚动的文本框
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, undo=True, font=("consolas", 10))
        self.text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.current_match_index = -1  # 当前匹配项索引
        self.matches = []  # 存储匹配项位置

        # 绑定快捷键
        self.text_area.bind("<Control-z>", lambda event: self.edit_undo())  # 撤销
        self.text_area.bind("<Control-slash>", self.toggle_comment)  # Windows/Linux
        self.text_area.bind("<Control-Key-/>", self.toggle_comment)  # macOS
        self.text_area.bind('<KeyRelease>', self.process_key)  # 处理空格
        self.text_area.bind("<Tab>", self.insert_spaces)  # 绑定 Tab 键
        self.text_area.bind("<Shift-Tab>", self.delete_spaces)  # 绑定 Shift+Tab 键
        self.text_area.bind('<Control-f>', self.find_text)  # 搜索
        self.text_area.bind('<Control-F>', self.find_text)  # 搜索
        # 绑定关键事件
        self.text_area.bind("<<Modified>>", self._on_text_modified)  # 绑定文本修改
        self.text_area.config(yscrollcommand=self._sync_scroll)  # 绑定滚动条
        # 初始化行号
        self._update_line_numbers()
        # 设置代码高亮
        self.color_delegator = ColorDelegator()
        self.percolator = Percolator(self.text_area)
        self.percolator.insertfilter(self.color_delegator)

    def _on_text_modified(self, event=None):
        """文本修改时触发行号更新"""
        if self.text_area.edit_modified():
            self._update_line_numbers()
            self._sync_scroll(self.text_area.yview()[0])  # 同步行号框的滚动位置
            self.text_area.edit_modified(False)

    def _sync_scroll(self, *args):
        """同步滚动位置"""
        self.line_number.yview_moveto(args[0])  # 同步行号框的滚动位置
        if hasattr(self.text_area, 'vbar') and len(args) == 2:
            self.text_area.vbar.set(*args)  # 更新滚动条

    def _update_line_numbers(self):
        """更新行号内容（只在文本变化时调用）"""
        # 获取总行数
        line_count = int(self.text_area.index('end-1c').split('.')[0])
        # 生成行号文本
        line_numbers = '\n'.join(
            str(i).rjust(len(str(line_count)))  # 右对齐
            for i in range(1, line_count + 1)
        )
        # 更新行号框
        self.line_number.config(state='normal')
        self.line_number.delete('1.0', tk.END)
        self.line_number.insert('1.0', line_numbers)
        self.line_number.config(state='disabled')
        # 动态调整宽度
        self.line_number.config(width=len(str(line_count)))

    def process_key(self, event):
        current_line_num, current_col_num = map(int, self.text_area.index(INSERT).split('.'))
        if event.keycode == 13:
            last_line_num = current_line_num - 1
            last_line = self.text_area.get(f'{last_line_num}.0', INSERT).rstrip()
            # 计算最后一行的前导空格数量
            num = len(last_line) - len(last_line.lstrip(' '))
            # 最后一行以冒号结束，或者冒号后面有#单行注释
            if (last_line.endswith(':') or
                (':' in last_line and last_line.split(':')[-1].strip().startswith('#'))):
                num = num + 4
            elif last_line.strip().startswith(('return','break','continue','pass','raise')):
                num = num - 4
            self.text_area.insert(INSERT,' '*num)

        elif event.keysym == 'BackSpace':
            current_line = self.text_area.get(f'{current_line_num}.0', f'{current_line_num}.{current_col_num}')
            num = len(current_line) - len(current_line.rstrip(' '))
            num2 = min(3, num)
            if num > 1 and (num + 1) % 4 == 0:
                self.text_area.delete(f'{current_line_num}.{current_col_num - num2}', f'{current_line_num}.{current_col_num}')
        # self.update_line_numbers()

    def insert_spaces(self, event):
        """将 Tab 键替换为 4 个空格，支持选中多行时批量右移"""
        try:
            start = self.text_area.index(tk.SEL_FIRST)
            end = self.text_area.index(tk.SEL_LAST)
            if start == end:
                # 没有选中文本时插入 4 个空格
                self.text_area.insert(tk.INSERT, ' ' * 4)
            else:
                # 转换为行号范围
                start_line = int(start.split('.')[0])
                end_line = int(end.split('.')[0])

                # 获取选中行的内容
                selected_lines = self.text_area.get(f'{start_line}.0', f'{end_line}.0 lineend').splitlines(keepends=True)

                # 创建新的内容
                new_lines = []
                for i in range(len(selected_lines)):
                    # 在选中行前插入 4 个空格
                    new_lines.append(' ' * 4 + selected_lines[i])

                # 删除选中的行并插入更新后的内容
                self.text_area.delete(f'{start_line}.0', f'{end_line}.0 lineend')
                self.text_area.insert(f'{start_line}.0', ''.join(new_lines))
                
                # 重新选中文本
                self.text_area.tag_add(tk.SEL, f'{start_line}.0', f'{end_line}.0 lineend')

        except tk.TclError:
            pass

        return "break"  # 阻止默认的 Tab 行为

    def delete_spaces(self, event):
        """Shift+Tab 事件处理，左移并保持光标相对位置"""
        try:
            start = self.text_area.index(tk.SEL_FIRST)
            end = self.text_area.index(tk.SEL_LAST)
            if start == end:
                # 无选区时的单行处理（关键修改部分）
                current_pos = self.text_area.index(tk.INSERT)
                line_num, column = map(int, current_pos.split('.'))  # 分解行列号
                line_start = f'{line_num}.0'
                line_end = f'{line_num}.end'

                # 获取当前行内容并计算删除量
                line_content = self.text_area.get(line_start, line_end)
                leading_spaces = len(line_content) - len(line_content.lstrip(' '))
                remove = min(4, leading_spaces)

                # 计算新光标列位置
                new_column = max(0, column - remove)  # 确保不出现负值

                # 执行删除和插入
                self.text_area.delete(line_start, line_end)
                self.text_area.insert(line_start, line_content[remove:])

                # 显式设置光标到计算后的新位置
                self.text_area.mark_set(tk.INSERT, f"{line_num}.{new_column}")
            else:
                # 多行处理逻辑（原有逻辑保留）
                start_line = int(start.split('.')[0])
                end_line = int(end.split('.')[0])

                selected_lines = self.text_area.get(f'{start_line}.0', f'{end_line}.0 lineend').splitlines(keepends=True)
                new_lines = []
                for line in selected_lines:
                    leading_spaces = len(line) - len(line.lstrip(' '))
                    remove = min(4, leading_spaces)
                    new_lines.append(line[remove:])

                self.text_area.delete(f'{start_line}.0', f'{end_line}.0 lineend')
                self.text_area.insert(f'{start_line}.0', ''.join(new_lines))
                
                # 重新选中文本
                self.text_area.tag_add(tk.SEL, f'{start_line}.0', f'{end_line}.0 lineend')

        except tk.TclError:
            pass

        return "break"

    def toggle_comment(self, event):
        """注释/取消注释的核心逻辑"""
        # 获取选中范围
        try:
            start = self.text_area.index(tk.SEL_FIRST)
            end = self.text_area.index(tk.SEL_LAST)
            if start == end:
                # 没有选中文本时默认处理当前行
                start = self.text_area.index(tk.INSERT + " linestart")
                end = self.text_area.index(tk.INSERT + " lineend")
        except tk.TclError:
            # 没有选中文本时默认处理当前行
            start = self.text_area.index(tk.INSERT + " linestart")
            end = self.text_area.index(tk.INSERT + " lineend")

        # 转换为行号范围
        start_line = int(start.split('.')[0])
        end_line = int(end.split('.')[0])

        # 检查是否有行未被注释
        any_uncommented = False
        for line_num in range(start_line, end_line + 1):
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            line_content = self.text_area.get(line_start, line_end)
            if not line_content.lstrip().startswith("#"):
                any_uncommented = True
                break

        # 逐行处理
        for line_num in range(start_line, end_line + 1):
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            line_content = self.text_area.get(line_start, line_end)

            if any_uncommented:
                # 添加注释：在行首的空格后插入 #
                leading_spaces = len(line_content) - len(line_content.lstrip())
                new_content = f"{' ' * leading_spaces}# {line_content.lstrip()}"
                self.text_area.delete(line_start, line_end)
                self.text_area.insert(line_start, new_content)
            else:
                # 取消注释：删除行首的 #
                stripped_content = line_content.lstrip()  # 去掉前导空格
                if stripped_content.startswith("#"):
                    # 只删除 #
                    new_content = stripped_content[1:].lstrip()  # 删除 # 后的空格
                    # 保留原有空格
                    new_content = line_content[:len(line_content) - len(stripped_content)] + new_content
                    self.text_area.delete(line_start, line_end)
                    self.text_area.insert(line_start, new_content)

        return "break"  # 阻止默认事件

    def search_result(self, key, ignore_case, search_toplevel, search_box):
        # 移除之前的高亮标记
        self.text_area.tag_remove('match', '1.0', "end")
        self.text_area.tag_remove('next', '1.0', "end")
        self.matches.clear()  # 清空匹配项
        matches_found = 0

        if not key.strip():  # 检查输入是否为空或仅空格
            # messagebox.showinfo("提示", "查找内容不能为空！", parent=search_toplevel)
            return

        start_pos = '1.0'
        found = False  # 是否找到至少一个匹配项
        while True:
            start_pos = self.text_area.search(
                key,
                start_pos,
                nocase=ignore_case,
                stopindex=tk.END
            )
            if not start_pos:
                break
            found = True
            end_pos = f"{start_pos}+{len(key)}c"
            self.text_area.tag_add('match', start_pos, end_pos)
            self.matches.append(start_pos)  # 保存匹配项位置
            matches_found += 1
            start_pos = end_pos  # 继续查找下一个匹配

        # 配置高亮样式
        self.text_area.tag_config('match', background='#4169E1', foreground='white')
        self.text_area.tag_config('next', background='#00FF00', foreground='black')

        # 更新窗口标题和反馈
        if not found:
            # messagebox.showinfo("提示", "未找到匹配内容", parent=search_toplevel)
            search_toplevel.title("未找到匹配内容")
        else:
            self.current_match_index = 0  # 重置当前匹配索引
            search_toplevel.title(f"找到 {matches_found} 个匹配项")

        search_box.focus_set()  # 保持输入框焦点

    def find_next(self):
        if not self.matches:
            return
        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        self.highlight_current_match()

    def find_previous(self):
        if not self.matches:
            return
        self.current_match_index = (self.current_match_index - 1) % len(self.matches)
        self.highlight_current_match()

    def highlight_current_match(self):
        # 移除之前的高亮
        self.text_area.tag_remove('match', '1.0', "end")
        self.text_area.tag_remove('next', '1.0', "end")

        if self.matches:
            current_match = self.matches[self.current_match_index]
            end_pos = f"{current_match}+{len(self.search_toplevel.search_entry.get())}c"

            # 高亮当前匹配项为绿底黑色
            self.text_area.tag_add('next', current_match, end_pos)
            self.text_area.see(current_match)  # 滚动到当前匹配项

            # 将其他匹配项高亮为蓝底白色
            for i, match in enumerate(self.matches):
                if i != self.current_match_index:
                    self.text_area.tag_add('match', match, f"{match}+{len(self.search_toplevel.search_entry.get())}c")

    def find_text(self, event=None):
        # 窗口复用逻辑：如果窗口已存在则置顶
        if hasattr(self, 'search_toplevel') and self.search_toplevel.winfo_exists():
            self.search_toplevel.lift()
            self.search_toplevel.search_entry.select_range(0, tk.END)  # 选中原有文本方便修改
            return "break"

        # 创建新窗口
        self.search_toplevel = Toplevel(self)
        self.search_toplevel.title("查找文本")
        self.search_toplevel.transient(self)
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
            self.matches.clear()  # 清空匹配项
            # self.tag_remove('match', '1.0', tk.END)
            # self.tag_remove('next', '1.0', tk.END)
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

if __name__ == "__main__":
    root = tk.Tk()
    root.title("My Text Editor")

    editor = TextEditor(root)
    editor.pack(expand=True, fill='both')

    root.mainloop()