import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.ui.basic_ui import BasicUI
from src.core.template_manager import TemplateManager
from src.core.csv_manager import CSVManager

import logging
logger = logging.getLogger(__name__)

class TabBEWGSED(ttk.Frame, BasicUI):
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

        listbox = self.template_manager.get_device_types(config="config_bewgsed")
        self.device_cb = self.add_combobox(frame, "设备类型：", row=0, col=0,listbox=listbox, inivar=-1)
        self.device_cb["combobox"].bind('<<ComboboxSelected>>', self.on_device_selected)

        self.template_cb = self.add_combobox(frame, "模板文件：", row=0, col=1,listbox=[], inivar=-1)
        self.template_cb['combobox'].bind('<<ComboboxSelected>>', self.on_template_selected)

        # 模板表格
        self.template_table = ttk.Treeview(frame, columns=("name","desc","type","addbyte","addbit"), show="headings", height=7)
        col_defs = {
            "name": ("名称", 100),
            "desc": ("描述", 130),
            "type": ("类型", 100),
            "addbyte": ("偏移字节", 80),
            "addbit": ("偏移位", 80),
        }      
        for col, (text, width) in col_defs.items():
            self.template_table.heading(col, text=text)
            self.template_table.column(col, width=width, anchor="center")
        self.template_table.grid(row=1, column=0, columnspan=4, sticky='nsew', pady=(9,5))

        # 让表格可伸缩
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def on_device_selected(self, event=None):
        """
        设备类型选择完成事件
        """
        device = self.device_cb['var'].get()
        self.template_cb['combobox']['values'] = self.template_manager.get_templates_by_device(device, config="config_bewgsed")
        #更新参数区的内容
        for row in self.template_table.get_children():  #清空表格
            self.template_table.delete(row)
        self.template_cb['var'].set("") #清空模板选择

    def on_template_selected(self,event=None):
        """
        点表模板选择完成事件
        """
        device = self.device_cb['var'].get()
        template = self.template_cb['var'].get()
        self.template_data = self.template_manager.load_template(device, template, config="config_bewgsed")
        self.refresh_template_table()

    def refresh_template_table(self):
        """
        模板数据加载到表格中
        """
        for row in self.template_table.get_children():
            self.template_table.delete(row)
        try:
            for item in self.template_data:
                self.template_table.insert('', 'end', values=(item['name'], item['desc'], item['type'], item['addbyte'], item['addbit']))
        except Exception as e:
            for row in self.template_table.get_children():
                self.template_table.delete(row)
            logger.error(f"加载模板异常{e}")
            messagebox.showwarning("加载出错", f"加载模板异常{e}", icon="error")

    # ---------------- CSV区 ----------------
    def create_csv_section(self, row, column):
        frame = ttk.LabelFrame(self, text="CSV 数据导入", padding=5)
        frame.grid(row=row, column=column, sticky='nsew', padx=6, pady=7)

        btn = ttk.Button(frame, text="选择CSV文件", command=self.load_csv_file)
        btn.grid(row=0, column=0, sticky='w')

        self.csv_table = ttk.Treeview(frame, columns=("code","desc","offset"), show="headings", height=8)
        cols = {"code": ("设备代号", 150), "desc": ("设备名称", 180), "offset": ("拼接地址", 120)}
        for col, (text, width) in cols.items():
            self.csv_table.heading(col, text=text)
            self.csv_table.column(col, width=width, anchor="center")
        self.csv_table.grid(row=1, column=0, sticky='nsew', padx=5, pady=(8,5))

        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

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
                self.csv_table.insert('', 'end', values=(row['设备代号'], row['设备描述'], row['拼接地址']))
        except Exception as e:
            logger.error(f"导入数据异常{e}")
            messagebox.showwarning("导入出错", f"导入数据异常{e}", icon="error")

    # ---------------- 参数区 ----------------
    def create_input_section(self, row, column, columnspan=1):
        frame = ttk.LabelFrame(self, text="参数输入", padding=10)
        frame.grid(row=row, column=column, columnspan=columnspan, sticky='ew', padx=10, pady=5)

        self.channel = self.add_input(frame, "所属通道", row=0, col=0, inivar="S127", entry_width=10) 
        self.dev_name = self.add_input(frame, "所属设备", row=0, col=1, inivar="PLC1", entry_width=10)
        self.drive_siemens = ["PLC_SIEMENS_S7_1200_TCP"]
        self.drive_ab = ["AB-ControlLogixTCP"]
        self.drive = self.add_combobox(frame, "驱动", row=0, col=2, listbox=self.drive_siemens, width=25)
        #self.drive["combobox"].bind('<<ComboboxSelected>>', self.on_link_selected)  # 选择完成事件   
        self.db_num = self.add_input(frame, "DB块号", row=0, col=3, inivar="3", entry_width=5)
        

    def on_link_selected(self, event=None):
        """
        链路选择完成事件
        """
        link_var = self.link["var"].get()
        if link_var == "以太网":
            self.link_com["frame"].grid_remove()
            self.link_ip["frame"].grid()
        elif link_var == "COM":
            self.link_ip["frame"].grid_remove()
            self.link_com["frame"].grid()

    # ---------------- 生成区 ----------------
    def create_generate_section(self, row, column, columnspan=1):
        frame = ttk.Frame(self)
        frame.grid(row=row, column=column, columnspan=columnspan, sticky='ew', padx=10, pady=5)
        btn = ttk.Button(frame, text="生成点表文件", command=self.on_generate_selected)
        btn.pack(anchor='center')

    def on_generate_selected(self):
        """
        生成文件按钮事件
        """
        if not getattr(self, 'template_data', None) or not getattr(self, 'csv_data', None):
            messagebox.showwarning("警告", "请先加载模板和CSV数据！")
            return
        inputs = {
            "channel": self.channel["var"].get(), #所属通道
            "dev_name": self.dev_name["var"].get(), #所属设备
            "drive": self.drive["var"].get(),   #驱动
            "db_num": self.db_num["var"].get(),  #DB块号
            "device": self.device_cb["var"].get(),  #设备类型
        }
        #执行数据处理
        self.csv_manager.rows_bewgsed(self.template_data, inputs)
        #文件名称
        file_name = f"{self.device_cb["var"].get()}_{self.template_cb["var"].get()[:-5]}"
        #输出文件
        output_path = self.csv_manager.generate_output("output_bewgsde", file_name)
        if output_path:
            messagebox.showinfo("生成成功", output_path)
