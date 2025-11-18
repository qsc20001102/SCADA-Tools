import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.ui.basic_ui import BasicUI
from src.core.template_manager import TemplateManager
from src.core.csv_manager import CSVManager

import logging
logger = logging.getLogger(__name__)

class TabKingSCDAD(ttk.Frame, BasicUI):
    def __init__(self, parent, base_dir):
        super().__init__(parent)
        self.template_manager = TemplateManager(base_dir)
        self.csv_manager = CSVManager(base_dir)
        self.main_ui()

    def main_ui(self):
        """布局 Tab 页面"""
        # 第一行：模板区 + CSV区
        self.create_template_section(row=0, column=0)
        self.create_csv_section(row=0, column=1)
        # 第二行：参数区
        self.create_input_section(row=1, column=0, columnspan=2)
        # 第三行：生成区
        self.create_generate_section(row=2, column=0, columnspan=2)
        # 设置行列可伸缩
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    # ---------------- 模板区 ----------------
    def create_template_section(self, row, column):
        frame = ttk.LabelFrame(self, text="配置文件选择", padding=5)
        frame.grid(row=row, column=column, sticky='nsew', padx=5, pady=5)

        self.device_cb = self.add_combobox(frame, "设备类型：", row=0, col=0,listbox=self.template_manager.get_device_types(), inivar=-1)
        self.device_cb["combobox"].bind('<<ComboboxSelected>>', self.on_device_selected)

        self.template_cb = self.add_combobox(frame, "模板文件：", row=0, col=1,listbox=[], inivar=-1)
        self.template_cb['combobox'].bind('<<ComboboxSelected>>', self.on_template_selected)

        # 模板表格
        self.template_table = ttk.Treeview(frame, columns=("name","desc","type","access","address"),show="headings", height=8)
        cols = {"name": ("名称", 100), "desc": ("描述", 130), "type": ("类型", 100),
                "access": ("读写", 80), "address": ("地址", 78)}
        for col, (text, width) in cols.items():
            self.template_table.heading(col, text=text)
            self.template_table.column(col, width=width, anchor="center")
        self.template_table.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=5)

        # 让表格可伸缩
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    # ---------------- CSV区 ----------------
    def create_csv_section(self, row, column):
        frame = ttk.LabelFrame(self, text="CSV 数据导入", padding=5)
        frame.grid(row=row, column=column, sticky='nsew', padx=5, pady=5)

        btn = ttk.Button(frame, text="选择CSV文件", command=self.load_csv_file)
        btn.grid(row=0, column=0, sticky='w')

        self.csv_table = ttk.Treeview(frame, columns=("code","desc","offset"), show="headings", height=8)
        cols = {"code": ("设备代号", 150), "desc": ("设备名称", 180), "offset": ("拼接地址", 120)}
        for col, (text, width) in cols.items():
            self.csv_table.heading(col, text=text)
            self.csv_table.column(col, width=width, anchor="center")
        self.csv_table.grid(row=1, column=0, sticky='nsew', pady=5)

        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    # ---------------- 参数区 ----------------
    def create_input_section(self, row, column, columnspan=1):
        frame = ttk.LabelFrame(self, text="参数输入", padding=10)
        frame.grid(row=row, column=column, columnspan=columnspan, sticky='ew', padx=10, pady=5)

        self.start_id = self.add_input(frame, "起始ID", row=0, col=0, inivar=1001) 
        self.dev_name = self.add_input(frame, "设备名称", row=0, col=1, inivar="PLC1")
        self.group_name = self.add_input(frame, "分组路径", row=0, col=2, inivar="TEST.一期")
        self.group_name_en = self.add_combobox(frame, "设备分组", row=0, col=3, listbox=["禁用", "启用"])

        self.link = self.add_combobox(frame, "采集链路", row=1, col=0, listbox=["以太网", "COM"])
        self.link["combobox"].bind('<<ComboboxSelected>>', self.on_link_selected)
        self.link_com = self.add_input(frame, "串口号", row=1, col=1, inivar="11")
        self.link_ip = self.add_input(frame, "IP地址", row=1, col=1, inivar="192.168.10.11") 

        self.deviceseries_siemens = ["S7-1500", "S7-1200", "S7-300(TCP)"]
        self.channeldriver_siemens = ["S71500Tcp", "S71200Tcp", "S7_TCP"]
        self.deviceseries_ab = ["AB-ControlLogixTCP"]
        self.channeldriver_ab = ["ControlLogix"]

        self.deviceseries = self.add_combobox(frame, "设备系列", row=2, col=0, listbox=self.deviceseries_siemens)
        self.channeldriver = self.add_combobox(frame, "通道驱动", row=2, col=1, listbox=self.channeldriver_siemens)
        self.db_num = self.add_input(frame, "DB块号", row=2, col=2, inivar="3")

    # ---------------- 生成区 ----------------
    def create_generate_section(self, row, column, columnspan=1):
        frame = ttk.Frame(self)
        frame.grid(row=row, column=column, columnspan=columnspan, sticky='ew', padx=10, pady=5)
        btn = ttk.Button(frame, text="生成点表文件", command=self.generate_csv)
        btn.pack(anchor='center')

    # ---------------- 链路选择事件 ----------------
    def on_link_selected(self, event=None):
        link_var = self.link["var"].get()
        if link_var == "以太网":
            self.link_com["frame"].grid_remove()
            self.link_ip["frame"].grid()
        elif link_var == "COM":
            self.link_ip["frame"].grid_remove()
            self.link_com["frame"].grid()

    # ---------------- CSV 文件操作 ----------------
    def load_csv_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return
        self.csv_data = self.csv_manager.load_csv(filepath)
        self.refresh_csv_table()

    def refresh_csv_table(self):
        for row in self.csv_table.get_children():
            self.csv_table.delete(row)
        try:
            for row in self.csv_data:
                self.csv_table.insert('', 'end', values=(row['设备代号'], row['设备描述'], row['拼接地址']))
        except Exception as e:
            logger.error(f"导入数据异常{e}")
            messagebox.showwarning("导入出错", f"导入数据异常{e}", icon="error")

    # ---------------- 模板操作 ----------------
    def on_device_selected(self, event=None):
        device = self.device_cb['var'].get()
        self.template_cb['combobox']['values'] = self.template_manager.get_templates_by_device(device)
        #更新参数区的内容
        if device == "SIEMENS" :
            for row in self.template_table.get_children():  #清空表格
                self.template_table.delete(row)
            self.template_cb['var'].set("") #清空模板选择
            self.deviceseries['combobox']['values'] = self.deviceseries_siemens #更新设备系列选项
            self.channeldriver['combobox']['values'] = self.channeldriver_siemens   #更新通道驱动选项
            self.deviceseries['var'].set(self.deviceseries_siemens[0])  #设置默认值
            self.channeldriver['var'].set(self.channeldriver_siemens[0])    #设置默认值
            self.db_num["frame"].grid() #显示DB块号输入框
        if device == "AB" :
            for row in self.template_table.get_children():
                self.template_table.delete(row)
            self.template_cb['var'].set("")
            self.deviceseries['combobox']['values'] = self.deviceseries_ab
            self.channeldriver['combobox']['values'] = self.channeldriver_ab
            self.deviceseries['var'].set(self.deviceseries_ab[0])
            self.channeldriver['var'].set(self.channeldriver_ab[0])
            self.db_num["frame"].grid_remove()  #隐藏DB块号输入框

    def on_template_selected(self, event=None):
        device = self.device_cb['var'].get()
        template = self.template_cb['var'].get()
        self.template_data = self.template_manager.load_template(device, template)
        self.refresh_template_table()

    def refresh_template_table(self):
        for row in self.template_table.get_children():
            self.template_table.delete(row)
        try:
            for item in self.template_data:
                self.template_table.insert('', 'end', values=(item['name'], item['desc'], item['type'], item['access'], item['address']))
        except Exception as e:
            logger.error(f"加载模板异常{e}")
            messagebox.showwarning("加载出错", f"加载模板异常{e}", icon="error")

    # ---------------- 生成 CSV ----------------
    def generate_csv(self):
        if not getattr(self, 'template_data', None) or not getattr(self, 'csv_data', None):
            messagebox.showwarning("警告", "请先加载模板和CSV数据！")
            return
        inputs = {
            "start_id": self.start_id["var"].get(),
            "ip": self.link_ip["var"].get(),
            "device_name": self.dev_name["var"].get(),
            "group_name": self.group_name["var"].get(),
            "link":self.link["var"].get(),
            "link_ip":self.link_ip["var"].get(),
            "link_com":self.link_com["var"].get(),
            "deviceseries": self.deviceseries["var"].get(),
            "channeldriver": self.channeldriver["var"].get(),
            "db_num": self.db_num["var"].get(),
            "device": self.device_cb["var"].get(),
            "group_name_en": self.group_name_en["var"].get()
        }
        output_path = self.csv_manager.generate_output(self.template_data, inputs)
        messagebox.showinfo("生成成功", output_path)
