import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio

from src.ui.basic_ui import BasicUI
from src.core.edgetts_manager import EdgeTTSManager
from src.core.csv_manager import CSVManager

import logging
logger = logging.getLogger(__name__)

class TabEdgeTTS(ttk.Frame, BasicUI):
    def __init__(self, parent, base_dir):
        super().__init__(parent)   
        self.csv_manager = CSVManager(base_dir)
        self.EdgeTTS = EdgeTTSManager(base_dir)
        try:
            asyncio.run(self.EdgeTTS.fetch_voices())
            self.list_voices = self.EdgeTTS.list_voices()
        except Exception as e:
            logger.error(f"获取语音列表失败: {e}")
            messagebox.showwarning("错误", "获取语音列表失败，请检查网络连接！", icon="error")
        self.main_ui()

    def main_ui(self):
        """布局 Tab 页面"""
        # 第一行：
        self.create_csv_section(row=0, column=0)
        self.create_input_section(row=0, column=1)

    # ---------------- CSV区 ----------------
    def create_csv_section(self, row, column):
        frame = ttk.LabelFrame(self, text="文本数据导入", padding=5)
        frame.grid(row=row, column=column, sticky='nsew', padx=5, pady=5)

        btn = ttk.Button(frame, text="选择CSV文件", command=self.load_csv_file)
        btn.grid(row=0, column=0, sticky='w')

        self.csv_table = ttk.Treeview(frame, columns=("text"), show="headings", height=13)
        cols = {"text": ("文本列表", 250)}
        for col, (text, width) in cols.items():
            self.csv_table.heading(col, text=text)
            self.csv_table.column(col, width=width, anchor="center")
        self.csv_table.grid(row=1, column=0, sticky='nsew', pady=5)


    def load_csv_file(self):
        """
        获取一个选择路径，并加载文件
        """
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return
        self.csv_data = self.csv_manager.load_csv(filepath)
        self.refresh_csv_table()

    def refresh_csv_table(self):
        """
        选择的SCV数据加载到表格中
        """
        for row in self.csv_table.get_children():
            self.csv_table.delete(row)
        try:
            for row in self.csv_data:
                self.csv_table.insert('', 'end', values=(row['文本']))
        except Exception as e:
            logger.error(f"导入数据异常{e}")
            messagebox.showwarning("导入出错", f"导入数据异常{e}", icon="error")

    # ---------------- 参数区 ----------------
    def create_input_section(self, row, column):
        frame = ttk.LabelFrame(self, text="语音参数", padding=10)
        frame.grid(row=row, column=column,  sticky='nsew', padx=10, pady=5)

        self.voices_com = self.add_combobox(frame, "语言", row=0, col=0, listbox=self.list_voices, width=30, inivar=510)
        self.voices_com["combobox"].bind('<<ComboboxSelected>>', self.on_voices_selected)
        #获取默认语言
        voice = self.voices_com["var"].get()
        #根据默认语言获取音色和风格
        self.list_styles = self.EdgeTTS.get_voice_styles(voice)
        self.list_roles = self.EdgeTTS.get_voice_roles(voice)
        self.style_com = self.add_combobox(frame, "风格", row=1, col=0, listbox=self.list_styles, width=20)
        self.role_com = self.add_combobox(frame, "角色", row=1, col=1, listbox=self.list_roles, width=20)
        self.on_voices_selected()

        self.rate_in = self.add_input(frame, "语速", row=2, col=0, inivar="20", entry_width=8)
        self.pitch_in = self.add_input(frame, "音高", row=2, col=1, inivar="5", entry_width=8)
        self.styledegree_in = self.add_input(frame, "风格强度", row=2, col=2, inivar="1.0", entry_width=8)

        self.text_in = self.add_input(frame, "语音文本", row=3, col=0, inivar="进水泵房液位高高报警", entry_width=55, colspan=3)

        #self.link = self.add_combobox(frame, "采集链路", row=1, col=0, listbox=["以太网", "COM"])
        #self.link["combobox"].bind('<<ComboboxSelected>>', self.on_link_selected)
        self.one_btn = ttk.Button(frame, text="单条语音生成", command=self.on_one_generate_selected)
        self.one_btn.grid(row=4, column=0, columnspan=3, sticky='nsew', pady=5)
        self.batch_btn = ttk.Button(frame, text="批量语音生成", command=self.on_batch_generate_selected)
        self.batch_btn.grid(row=5, column=0, columnspan=3, sticky='nsew', pady=5)

    def on_voices_selected(self, event=None):
        """
        语音选择完成事件
        """
        voice = self.voices_com["var"].get()
        self.list_styles = self.EdgeTTS.get_voice_styles(voice)
        self.list_roles = self.EdgeTTS.get_voice_roles(voice)
        self.style_com['combobox']['values'] = self.list_styles
        self.role_com['combobox']['values'] = self.list_roles

        if self.list_styles:
            self.style_com['var'].set(self.list_styles[0]) 
        else:
            self.style_com['var'].set("") 

        if self.list_roles:
            self.role_com['var'].set(self.list_roles[0]) 
        else:
            self.role_com['var'].set("") 

    def _format_percentage(value):
        """
        将数字或数字字符串格式化为带符号百分比形式。
        
        规则：
        - 正数或无符号数字前加 '+'，负数保留 '-'。
        - 后面加上 '%'
        
        示例：
        format_percentage("20") -> "+20%"
        format_percentage("-20") -> "-20%"
        """
        # 将输入转换为整数
        num = int(value)
        # 根据正负号添加前缀
        if num >= 0:
            return f"+{num}%"
        else:
            return f"{num}%"

    def on_one_generate_selected(self):
        """
        生成单条语音按钮事件
        """
        if self.text_in['var'].get() == "":
            messagebox.showwarning("警告", "请先输入要转化为语音的文本！")
            return
        output_path = asyncio.run(self.EdgeTTS.generate_speech(
            text=self.text_in['var'].get(),
            voice=self.voices_com['var'].get()
            ))
        if not output_path:
            messagebox.showwarning("错误", "语音生成失败！")
        else:
            messagebox.showinfo("生成成功", output_path)

    def on_batch_generate_selected(self):
        """
        生成多条语音按钮事件
        """
        if  not getattr(self, 'csv_data', None):
            messagebox.showwarning("警告", "请先加载语音文本的SCV文件！")
            return
        output_dir, count = asyncio.run(self.EdgeTTS.generate_batch(
            text_list=[item.get("文本", "") for item in self.csv_manager.csv_data],
            voice=self.voices_com['var'].get()
        ))
        if  count == 0:
            messagebox.showwarning("错误", "语音生成失败！")
        else:
            messagebox.showinfo("生成成功", f"生成完成：{count}条语音，文件夹路径：{output_dir}")
